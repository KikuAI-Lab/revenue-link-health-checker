from __future__ import annotations

import socket
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


REDIRECT_STATUSES = {301, 302, 303, 307, 308}
AMBIGUOUS_HTTP_STATUSES = {401, 403, 429}
AMBIGUOUS_BODY_MARKERS = {
    "captcha": "CAPTCHA-like response body",
    "verify you are human": "human-verification response body",
    "access denied": "access-denied response body",
    "not available in your country": "geo-dependent response body",
    "sign in to continue": "login-gated response body",
}


@dataclass(frozen=True)
class CheckerConfig:
    max_redirects: int = 10
    timeout_seconds: float = 10.0
    retries: int = 1


@dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: Mapping[str, str]
    body: bytes


@dataclass(frozen=True)
class CheckResult:
    normalized_url: str
    final_url: str
    redirect_chain: tuple[str, ...]
    observed_status: str
    candidate_issue_type: str
    automated_verdict: str
    blocked_or_ambiguous: bool
    evidence_note: str
    check_time_seconds: float
    estimated_direct_cost_usd: float = 0.0


Transport = Callable[[str, float], HttpResponse]


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(
        self,
        req: Request,
        fp: object,
        code: int,
        msg: str,
        headers: Mapping[str, str],
        newurl: str,
    ) -> None:
        return None


def normalize_url(url: str) -> str:
    parsed = urlsplit(url.strip())
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"
    return urlunsplit((scheme, netloc, path, parsed.query, ""))


def check_url(
    url: str,
    config: CheckerConfig | None = None,
    *,
    transport: Transport | None = None,
) -> CheckResult:
    effective_config = config or CheckerConfig()
    effective_transport = transport or _fetch_once
    normalized_url = normalize_url(url)
    current_url = normalized_url
    chain: list[str] = []
    visited: set[str] = set()
    redirects_followed = 0
    started_at = time.monotonic()

    while True:
        if current_url in visited:
            return _candidate_result(
                normalized_url,
                current_url,
                chain + [current_url],
                "redirect_loop",
                "Redirect loop detected",
                started_at,
            )

        visited.add(current_url)
        chain.append(current_url)
        response, error = _fetch_with_retries(current_url, effective_config, effective_transport)
        if error is not None:
            observed_status = "timeout" if _is_timeout(error) else "network_error"
            return _ambiguous_result(
                normalized_url,
                current_url,
                chain,
                observed_status,
                f"Network result is ambiguous: {error}",
                started_at,
            )

        if response is None:
            return _ambiguous_result(
                normalized_url,
                current_url,
                chain,
                "network_error",
                "Transport returned no response",
                started_at,
            )

        status = response.status
        if status in REDIRECT_STATUSES:
            location = response.headers.get("Location") or response.headers.get("location")
            if not location:
                return _candidate_result(
                    normalized_url,
                    current_url,
                    chain,
                    "redirect_missing_location",
                    f"HTTP {status} response omitted Location header",
                    started_at,
                )
            if redirects_followed >= effective_config.max_redirects:
                return _candidate_result(
                    normalized_url,
                    current_url,
                    chain,
                    "excessive_redirect_chain",
                    f"Redirect chain exceeded {effective_config.max_redirects} hops",
                    started_at,
                )
            current_url = normalize_url(urljoin(current_url, location))
            redirects_followed += 1
            continue

        if status in AMBIGUOUS_HTTP_STATUSES:
            return _ambiguous_result(
                normalized_url,
                current_url,
                chain,
                f"HTTP {status}",
                f"HTTP {status} can indicate access controls or rate limiting",
                started_at,
            )

        if status in {404, 410}:
            return _candidate_result(
                normalized_url,
                current_url,
                chain,
                f"http_{status}",
                f"HTTP {status} returned by final destination",
                started_at,
                observed_status=f"HTTP {status}",
            )

        if status >= 500:
            return _candidate_result(
                normalized_url,
                current_url,
                chain,
                "persistent_5xx",
                f"HTTP {status} persisted after configured retry",
                started_at,
                observed_status=f"HTTP {status}",
            )

        body = response.body[:131_072].decode("utf-8", errors="ignore").lower()
        for marker, note in AMBIGUOUS_BODY_MARKERS.items():
            if marker in body:
                return _ambiguous_result(
                    normalized_url,
                    current_url,
                    chain,
                    f"HTTP {status}",
                    note,
                    started_at,
                )

        return CheckResult(
            normalized_url=normalized_url,
            final_url=current_url,
            redirect_chain=tuple(chain),
            observed_status=f"HTTP {status}",
            candidate_issue_type="",
            automated_verdict="ok",
            blocked_or_ambiguous=False,
            evidence_note="Final destination responded without a deterministic issue marker",
            check_time_seconds=_elapsed(started_at),
        )


def _fetch_with_retries(
    url: str,
    config: CheckerConfig,
    transport: Transport,
) -> tuple[HttpResponse | None, BaseException | None]:
    last_error: BaseException | None = None
    for attempt in range(config.retries + 1):
        try:
            response = transport(url, config.timeout_seconds)
        except (TimeoutError, socket.timeout, URLError) as error:
            last_error = error
            if attempt < config.retries:
                continue
            return None, error
        if response.status >= 500 and attempt < config.retries:
            continue
        return response, None
    return None, last_error


def _fetch_once(url: str, timeout_seconds: float) -> HttpResponse:
    opener = build_opener(_NoRedirectHandler())
    request = Request(url, headers={"User-Agent": "RevenueLinkHealthP0/0.1"})
    try:
        with opener.open(request, timeout=timeout_seconds) as response:
            return HttpResponse(response.status, dict(response.headers.items()), response.read(131_072))
    except HTTPError as error:
        try:
            return HttpResponse(error.code, dict(error.headers.items()), error.read(131_072))
        finally:
            error.close()


def _candidate_result(
    normalized_url: str,
    final_url: str,
    chain: list[str],
    issue_type: str,
    evidence_note: str,
    started_at: float,
    *,
    observed_status: str | None = None,
) -> CheckResult:
    return CheckResult(
        normalized_url=normalized_url,
        final_url=final_url,
        redirect_chain=tuple(chain),
        observed_status=observed_status or issue_type,
        candidate_issue_type=issue_type,
        automated_verdict="candidate_issue",
        blocked_or_ambiguous=False,
        evidence_note=evidence_note,
        check_time_seconds=_elapsed(started_at),
    )


def _ambiguous_result(
    normalized_url: str,
    final_url: str,
    chain: list[str],
    observed_status: str,
    evidence_note: str,
    started_at: float,
) -> CheckResult:
    return CheckResult(
        normalized_url=normalized_url,
        final_url=final_url,
        redirect_chain=tuple(chain),
        observed_status=observed_status,
        candidate_issue_type="",
        automated_verdict="blocked_or_ambiguous",
        blocked_or_ambiguous=True,
        evidence_note=evidence_note,
        check_time_seconds=_elapsed(started_at),
    )


def _is_timeout(error: BaseException) -> bool:
    if isinstance(error, (TimeoutError, socket.timeout)):
        return True
    return isinstance(error, URLError) and isinstance(error.reason, (TimeoutError, socket.timeout))


def _elapsed(started_at: float) -> float:
    return round(time.monotonic() - started_at, 6)
