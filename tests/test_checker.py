from __future__ import annotations

import unittest

from linkhealth.checker import CheckerConfig, HttpResponse, check_url, normalize_url
from tests.support import FixtureServer


class NormalizeUrlTests(unittest.TestCase):
    def test_preserves_query_parameters_and_removes_fragment(self) -> None:
        normalized = normalize_url("HTTPS://Example.COM/product?tag=owner-20&ref=a#details")

        self.assertEqual(normalized, "https://example.com/product?tag=owner-20&ref=a")


class CheckUrlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.routes = {
            "/ok": (200, {"Content-Type": "text/plain"}, b"ok"),
            "/redirect": (302, {"Location": "/ok?tag=owner-20"}, b""),
            "/not-found": (404, {}, b"missing"),
            "/gone": (410, {}, b"gone"),
            "/forbidden": (403, {}, b"forbidden"),
            "/rate-limit": (429, {}, b"too many requests"),
            "/captcha": (200, {"Content-Type": "text/html"}, b"<html>captcha challenge</html>"),
            "/loop-a": (302, {"Location": "/loop-b"}, b""),
            "/loop-b": (302, {"Location": "/loop-a"}, b""),
            "/chain-1": (302, {"Location": "/chain-2"}, b""),
            "/chain-2": (302, {"Location": "/chain-3"}, b""),
            "/chain-3": (302, {"Location": "/ok"}, b""),
        }

    def test_captures_redirect_chain_and_final_url(self) -> None:
        with FixtureServer(self.routes) as server:
            result = check_url(f"{server.base_url}/redirect")

        self.assertEqual(result.automated_verdict, "ok")
        self.assertEqual(result.redirect_chain[0], f"{server.base_url}/redirect")
        self.assertEqual(result.final_url, f"{server.base_url}/ok?tag=owner-20")
        self.assertEqual(result.observed_status, "HTTP 200")

    def test_classifies_not_found_as_candidate_issue(self) -> None:
        with FixtureServer(self.routes) as server:
            result = check_url(f"{server.base_url}/not-found")

        self.assertEqual(result.automated_verdict, "candidate_issue")
        self.assertEqual(result.candidate_issue_type, "http_404")
        self.assertFalse(result.blocked_or_ambiguous)

    def test_classifies_gone_as_candidate_issue(self) -> None:
        with FixtureServer(self.routes) as server:
            result = check_url(f"{server.base_url}/gone")

        self.assertEqual(result.candidate_issue_type, "http_410")

    def test_retries_and_classifies_persistent_5xx(self) -> None:
        attempts: list[str] = []

        def transport(url: str, timeout_seconds: float) -> HttpResponse:
            attempts.append(url)
            return HttpResponse(500, {}, b"server error")

        result = check_url(
            "https://example.com/error",
            CheckerConfig(retries=1),
            transport=transport,
        )

        self.assertEqual(len(attempts), 2)
        self.assertEqual(result.candidate_issue_type, "persistent_5xx")

    def test_classifies_redirect_loop(self) -> None:
        with FixtureServer(self.routes) as server:
            result = check_url(f"{server.base_url}/loop-a")

        self.assertEqual(result.candidate_issue_type, "redirect_loop")

    def test_classifies_excessive_redirect_chain(self) -> None:
        with FixtureServer(self.routes) as server:
            result = check_url(
                f"{server.base_url}/chain-1",
                CheckerConfig(max_redirects=1),
            )

        self.assertEqual(result.candidate_issue_type, "excessive_redirect_chain")

    def test_classifies_http_blocks_as_ambiguous(self) -> None:
        with FixtureServer(self.routes) as server:
            forbidden = check_url(f"{server.base_url}/forbidden")
            limited = check_url(f"{server.base_url}/rate-limit")

        self.assertEqual(forbidden.automated_verdict, "blocked_or_ambiguous")
        self.assertEqual(limited.automated_verdict, "blocked_or_ambiguous")
        self.assertTrue(forbidden.blocked_or_ambiguous)

    def test_classifies_captcha_body_as_ambiguous(self) -> None:
        with FixtureServer(self.routes) as server:
            result = check_url(f"{server.base_url}/captcha")

        self.assertEqual(result.automated_verdict, "blocked_or_ambiguous")
        self.assertIn("CAPTCHA", result.evidence_note)

    def test_classifies_timeout_as_ambiguous(self) -> None:
        def transport(url: str, timeout_seconds: float) -> HttpResponse:
            raise TimeoutError("timed out")

        result = check_url("https://example.com/slow", transport=transport)

        self.assertEqual(result.automated_verdict, "blocked_or_ambiguous")
        self.assertEqual(result.observed_status, "timeout")


if __name__ == "__main__":
    unittest.main()
