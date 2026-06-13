from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from .models import SampleInput
from .repair import RepairAction


_MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[([^\]]{1,300})\]\((https?://[^)\s]+)\)")
_SPACES_RE = re.compile(r"\s+")
_PREFIX_RE = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class PatchResult:
    text: str
    replacements_applied: int
    skipped_actions: int


@dataclass(frozen=True)
class _DocumentLink:
    url: str
    context: str


class _AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[_DocumentLink] = []
        self._active_href = ""
        self._active_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a" or self._active_href:
            return
        href = _attr_value(attrs, "href")
        if not href or not _is_http_url(href):
            return
        self._active_href = href
        self._active_text = []

    def handle_data(self, data: str) -> None:
        if self._active_href:
            self._active_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or not self._active_href:
            return
        self.links.append(
            _DocumentLink(
                url=self._active_href,
                context=_clean_context(" ".join(self._active_text)) or self._active_href,
            )
        )
        self._active_href = ""
        self._active_text = []


def extract_document_links(
    text: str,
    *,
    filename: str,
    lane: str = "web_affiliate",
    consent_basis: str = "local_file",
) -> list[SampleInput]:
    links = _extract_markdown_links(text) + _extract_html_links(text)
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
    for match in _MARKDOWN_LINK_RE.finditer(text):
        context = _clean_context(match.group(1)) or match.group(2)
        url = match.group(2)
        if _is_http_url(url):
            links.append(_DocumentLink(url=url, context=context))
    return links


def _extract_html_links(text: str) -> list[_DocumentLink]:
    parser = _AnchorParser()
    parser.feed(text)
    parser.close()
    return parser.links


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


def _sample_prefix(filename: str) -> str:
    stem = Path(filename).stem.lower() or "document"
    prefix = _PREFIX_RE.sub("-", stem).strip("-")
    return prefix or "document"
