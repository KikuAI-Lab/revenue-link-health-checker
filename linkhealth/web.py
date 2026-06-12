from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser


DEFAULT_USER_AGENT = "RevenueLinkHealthP0/0.1"
SKIPPED_CONTAINERS = {"footer", "header", "nav", "noscript", "script", "style", "svg"}
SOCIAL_HOSTS = {
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "t.me",
    "twitter.com",
    "x.com",
    "youtube.com",
}
ASSET_SUFFIXES = {
    ".css",
    ".gif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".js",
    ".mp4",
    ".pdf",
    ".png",
    ".svg",
    ".webm",
    ".webp",
    ".woff",
    ".woff2",
    ".xml",
    ".zip",
}


class WebCollectionError(RuntimeError):
    """Raised when a public page cannot be collected safely."""


class RobotsDeniedError(WebCollectionError):
    """Raised when robots.txt denies collection of a page."""


class RobotsUnavailableError(WebCollectionError):
    """Raised when robots.txt cannot be evaluated safely."""


@dataclass(frozen=True)
class CollectedLink:
    source_reference: str
    source_context: str
    original_url: str


class _ContentLinkParser(HTMLParser):
    def __init__(self, page_url: str, max_links: int) -> None:
        super().__init__(convert_charrefs=True)
        self.page_url = page_url
        self.max_links = max_links
        self.page_host = urlsplit(page_url).hostname
        self.skip_depth = 0
        self.active_href: str | None = None
        self.active_text: list[str] = []
        self.links: list[CollectedLink] = []
        self.seen: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in SKIPPED_CONTAINERS:
            self.skip_depth += 1
            return
        if tag != "a" or self.skip_depth or len(self.links) >= self.max_links:
            return
        href = dict(attrs).get("href")
        if href:
            self.active_href = href
            self.active_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.active_href is not None:
            self._append_active_link()
            self.active_href = None
            self.active_text = []
        if tag in SKIPPED_CONTAINERS and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.active_href is not None and not self.skip_depth:
            self.active_text.append(data)

    def _append_active_link(self) -> None:
        if len(self.links) >= self.max_links:
            return
        absolute_url = urljoin(self.page_url, self.active_href or "")
        if not _is_external_content_url(absolute_url, self.page_host):
            return
        normalized = _without_fragment(absolute_url)
        if normalized in self.seen:
            return
        self.seen.add(normalized)
        context = " ".join("".join(self.active_text).split())
        self.links.append(
            CollectedLink(
                source_reference=self.page_url,
                source_context=context,
                original_url=normalized,
            )
        )


def extract_content_links(html: str, page_url: str, *, max_links: int = 150) -> list[CollectedLink]:
    parser = _ContentLinkParser(page_url, max_links)
    parser.feed(html)
    parser.close()
    return parser.links


def collect_public_page_links(
    page_url: str,
    *,
    max_links: int = 150,
    timeout_seconds: float = 10.0,
    user_agent: str = DEFAULT_USER_AGENT,
) -> list[CollectedLink]:
    robots_url = _robots_url(page_url)
    robots_status, robots_body = _fetch_text(robots_url, timeout_seconds, user_agent)
    if robots_status == 404:
        allowed = True
    elif robots_status == 200:
        parser = RobotFileParser()
        parser.set_url(robots_url)
        parser.parse(robots_body.splitlines())
        allowed = parser.can_fetch(user_agent, page_url)
    else:
        raise RobotsUnavailableError(f"cannot evaluate robots.txt: HTTP {robots_status}")
    if not allowed:
        raise RobotsDeniedError(f"robots.txt disallows {page_url}")

    page_status, page_body = _fetch_text(page_url, timeout_seconds, user_agent)
    if page_status != 200:
        raise WebCollectionError(f"public page fetch failed: HTTP {page_status}")
    return extract_content_links(page_body, page_url, max_links=max_links)


def _fetch_text(url: str, timeout_seconds: float, user_agent: str) -> tuple[int, str]:
    request = Request(url, headers={"User-Agent": user_agent})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            return response.status, response.read(524_288).decode("utf-8", errors="ignore")
    except HTTPError as error:
        try:
            return error.code, error.read(524_288).decode("utf-8", errors="ignore")
        finally:
            error.close()
    except URLError as error:
        raise RobotsUnavailableError(f"public fetch failed for {url}: {error}") from error


def _robots_url(page_url: str) -> str:
    parsed = urlsplit(page_url)
    return urlunsplit((parsed.scheme, parsed.netloc, "/robots.txt", "", ""))


def _without_fragment(url: str) -> str:
    parsed = urlsplit(url)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, parsed.query, ""))


def _is_external_content_url(url: str, page_host: str | None) -> bool:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False
    hostname = parsed.hostname.lower()
    if hostname == page_host:
        return False
    if hostname in SOCIAL_HOSTS or any(hostname.endswith(f".{host}") for host in SOCIAL_HOSTS):
        return False
    path = parsed.path.lower()
    return not any(path.endswith(suffix) for suffix in ASSET_SUFFIXES)
