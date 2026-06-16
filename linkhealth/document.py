from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .models import SampleInput
from .repair import RepairAction


_MARKDOWN_TARGET_RE = re.compile(r"(?<!!)\[([^\]]{1,300})\]\(([^)\s]+)\)")
_HTML_HREF_RE = re.compile(r"""\bhref\s*=\s*(["'])[^"']+\1""", re.IGNORECASE)
_PLAIN_TEXT_URL_RE = re.compile(r"https?://[^\s<>'\"`]+")
_SPACES_RE = re.compile(r"\s+")
_PREFIX_RE = re.compile(r"[^a-z0-9]+")
_TRAILING_URL_PUNCTUATION = ".,;:!?)]}"
_AFFILIATE_TRACKING_PARAMS = {
    "aff",
    "affid",
    "affiliate",
    "affiliate_id",
    "ascsubtag",
    "camp",
    "clickid",
    "creative",
    "irclickid",
    "linkcode",
    "tag",
    "utm_campaign",
    "utm_content",
    "utm_medium",
    "utm_source",
    "utm_term",
}


@dataclass(frozen=True)
class PatchResult:
    text: str
    replacements_applied: int
    skipped_actions: int


@dataclass(frozen=True)
class DocumentFinding:
    sample_id: str
    source_reference: str
    source_context: str
    original_url: str
    issue_type: str
    severity: str
    recommended_action: str
    evidence: str
    network_free: bool = True


@dataclass(frozen=True)
class _DocumentLink:
    url: str
    context: str


class _AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[_DocumentLink] = []
        self.targets: list[_DocumentLink] = []
        self._active_href = ""
        self._active_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a" or self._active_href:
            return
        href = _attr_value(attrs, "href")
        if not href:
            return
        self._active_href = href
        self._active_text = []

    def handle_data(self, data: str) -> None:
        if self._active_href:
            self._active_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or not self._active_href:
            return
        link = _DocumentLink(
            url=self._active_href,
            context=_clean_context(" ".join(self._active_text)) or self._active_href,
        )
        self.targets.append(link)
        if _is_http_url(self._active_href):
            self.links.append(link)
        self._active_href = ""
        self._active_text = []


def diagnose_document_links(text: str, *, filename: str) -> list[DocumentFinding]:
    samples = extract_document_links(text, filename=filename)
    sample_ids_by_url: dict[str, str] = {}
    contexts_by_url: dict[str, str] = {}
    for sample in samples:
        sample_ids_by_url.setdefault(sample.original_url, sample.sample_id)
        contexts_by_url.setdefault(sample.original_url, sample.source_context)

    raw_targets = _extract_markdown_targets(text) + _extract_html_targets(text)
    findings: list[DocumentFinding] = []
    prefix = _sample_prefix(filename)
    unsupported_index = 0

    seen_unsupported: set[str] = set()
    for target in raw_targets:
        issue_type = _unsupported_target_issue_type(target.url)
        if not issue_type or target.url in seen_unsupported:
            continue
        seen_unsupported.add(target.url)
        unsupported_index += 1
        findings.append(
            DocumentFinding(
                sample_id=f"{prefix}-local-{unsupported_index:03d}",
                source_reference=filename,
                source_context=target.context,
                original_url=target.url,
                issue_type=issue_type,
                severity="warning",
                recommended_action="Review this link target manually before publishing.",
                evidence=f"Unsupported or malformed non-empty link target: {target.url}",
            )
        )

    for sample in samples:
        parsed = urlsplit(sample.original_url)
        if parsed.scheme == "http" and not _is_local_or_private_host(parsed.hostname or ""):
            findings.append(
                DocumentFinding(
                    sample_id=sample.sample_id,
                    source_reference=sample.source_reference,
                    source_context=sample.source_context,
                    original_url=sample.original_url,
                    issue_type="insecure_http_url",
                    severity="warning",
                    recommended_action="Replace with the HTTPS version when the destination supports it.",
                    evidence="External commercial-looking destination uses http://.",
                )
            )
        tracking_params = _tracking_params(sample.original_url)
        if tracking_params:
            findings.append(
                DocumentFinding(
                    sample_id=sample.sample_id,
                    source_reference=sample.source_reference,
                    source_context=sample.source_context,
                    original_url=sample.original_url,
                    issue_type="affiliate_tracking_parameter",
                    severity="info",
                    recommended_action=(
                        "Verify that the tracking parameters are intentional and belong to this page."
                    ),
                    evidence=f"Tracking parameters present: {', '.join(tracking_params)}.",
                )
            )

    normalized_groups: dict[str, list[str]] = {}
    for sample in samples:
        normalized = _without_tracking_params(sample.original_url)
        if normalized != sample.original_url:
            normalized_groups.setdefault(normalized, []).append(sample.original_url)

    for normalized_url, originals in normalized_groups.items():
        unique_originals = list(dict.fromkeys(originals))
        if len(unique_originals) < 2:
            continue
        first_url = unique_originals[0]
        findings.append(
            DocumentFinding(
                sample_id=sample_ids_by_url.get(first_url, f"{prefix}-duplicate-001"),
                source_reference=filename,
                source_context=contexts_by_url.get(first_url, first_url),
                original_url=first_url,
                issue_type="duplicate_tracking_variant",
                severity="warning",
                recommended_action=(
                    "Review these tracked variants manually and consolidate them if they should point to the same recommendation."
                ),
                evidence=(
                    f"{len(unique_originals)} links normalize to {normalized_url} after tracking parameters are removed."
                ),
            )
        )

    return sorted(findings, key=lambda finding: (finding.issue_type, finding.sample_id, finding.original_url))


def extract_document_links(
    text: str,
    *,
    filename: str,
    lane: str = "web_affiliate",
    consent_basis: str = "local_file",
) -> list[SampleInput]:
    links = _extract_markdown_links(text) + _extract_html_links(text) + _extract_plain_text_links(text)
    samples: list[SampleInput] = []
    seen: set[tuple[str, str]] = set()
    prefix = _sample_prefix(filename)
    for link in links:
        key = (link.url, link.context)
        if key in seen:
            continue
        seen.add(key)
        samples.append(
            SampleInput(
                sample_id=f"{prefix}-{len(samples) + 1:03d}",
                lane=lane,
                consent_basis=consent_basis,
                source_reference=filename,
                source_context=link.context,
                original_url=link.url,
            )
        )
    return samples


def patch_document(text: str, actions: list[RepairAction]) -> PatchResult:
    patched = text
    replacements_applied = 0
    skipped_actions = 0
    for action in actions:
        if action.action != "replace_with_url" or not action.replacement_url:
            skipped_actions += 1
            continue
        if action.original_url not in patched:
            skipped_actions += 1
            continue
        patched = patched.replace(action.original_url, action.replacement_url)
        replacements_applied += 1
    return PatchResult(
        text=patched,
        replacements_applied=replacements_applied,
        skipped_actions=skipped_actions,
    )


def _extract_markdown_links(text: str) -> list[_DocumentLink]:
    links: list[_DocumentLink] = []
    for link in _extract_markdown_targets(text):
        context = _clean_context(link.context) or link.url
        url = link.url
        if _is_http_url(url):
            links.append(_DocumentLink(url=url, context=context))
    return links


def _extract_markdown_targets(text: str) -> list[_DocumentLink]:
    links: list[_DocumentLink] = []
    for match in _MARKDOWN_TARGET_RE.finditer(text):
        context = _clean_context(match.group(1)) or match.group(2)
        links.append(_DocumentLink(url=match.group(2).strip(), context=context))
    return links


def _extract_html_links(text: str) -> list[_DocumentLink]:
    return [target for target in _extract_html_targets(text) if _is_http_url(target.url)]


def _extract_html_targets(text: str) -> list[_DocumentLink]:
    parser = _AnchorParser()
    parser.feed(text)
    parser.close()
    return parser.targets


def _extract_plain_text_links(text: str) -> list[_DocumentLink]:
    scrubbed = _MARKDOWN_TARGET_RE.sub(lambda match: match.group(1), text)
    scrubbed = _HTML_HREF_RE.sub("", scrubbed)
    links: list[_DocumentLink] = []
    for match in _PLAIN_TEXT_URL_RE.finditer(scrubbed):
        url = _strip_trailing_url_punctuation(match.group(0))
        if _is_http_url(url):
            links.append(_DocumentLink(url=url, context=url))
    return links


def _attr_value(attrs: list[tuple[str, str | None]], name: str) -> str:
    for attr_name, attr_value in attrs:
        if attr_name.lower() == name and attr_value:
            return attr_value.strip()
    return ""


def _clean_context(value: str) -> str:
    return _SPACES_RE.sub(" ", value).strip()


def _is_http_url(value: str) -> bool:
    parsed = urlsplit(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _unsupported_target_issue_type(value: str) -> str:
    if not value:
        return ""
    parsed = urlsplit(value)
    if parsed.scheme in {"http", "https"}:
        return "" if parsed.netloc else "malformed_link_target"
    if parsed.scheme:
        return "unsupported_link_target"
    if value.startswith(("#", "/", "./", "../")):
        return ""
    if "." in value:
        return "malformed_link_target"
    return ""


def _tracking_params(value: str) -> list[str]:
    parsed = urlsplit(value)
    names = []
    for name, _value in parse_qsl(parsed.query, keep_blank_values=True):
        lowered = name.lower()
        if lowered in _AFFILIATE_TRACKING_PARAMS:
            names.append(name)
    return sorted(dict.fromkeys(names), key=str.lower)


def _without_tracking_params(value: str) -> str:
    parsed = urlsplit(value)
    kept_params = [
        (name, param_value)
        for name, param_value in parse_qsl(parsed.query, keep_blank_values=True)
        if name.lower() not in _AFFILIATE_TRACKING_PARAMS
    ]
    return urlunsplit(
        (
            parsed.scheme,
            parsed.netloc.lower(),
            parsed.path,
            urlencode(kept_params, doseq=True),
            parsed.fragment,
        )
    )


def _is_local_or_private_host(host: str) -> bool:
    lowered = host.lower()
    return (
        lowered in {"localhost", "127.0.0.1", "::1"}
        or lowered.startswith("127.")
        or lowered.startswith("10.")
        or lowered.startswith("192.168.")
        or lowered.endswith(".local")
    )


def _strip_trailing_url_punctuation(value: str) -> str:
    return value.rstrip(_TRAILING_URL_PUNCTUATION)


def _sample_prefix(filename: str) -> str:
    stem = Path(filename).stem.lower() or "document"
    prefix = _PREFIX_RE.sub("-", stem).strip("-")
    return prefix or "document"
