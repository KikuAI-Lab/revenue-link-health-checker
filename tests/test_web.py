from __future__ import annotations

import unittest

from linkhealth.web import RobotsDeniedError, collect_public_page_links, extract_content_links
from tests.support import FixtureServer


class ExtractContentLinksTests(unittest.TestCase):
    def test_returns_only_external_http_content_links(self) -> None:
        html = """
        <html>
          <body>
            <nav><a href="https://merchant.example/nav">Nav merchant</a></nav>
            <main>
              <a href="https://merchant.example/product?tag=owner-20">Recommended camera</a>
              <a href="/internal">Internal</a>
              <a href="mailto:hello@example.com">Mail</a>
              <a href="https://twitter.com/example">Social</a>
              <a href="https://cdn.example/image.jpg">Image</a>
              <a href="https://tools.example/pricing">Tool pricing</a>
            </main>
          </body>
        </html>
        """

        links = extract_content_links(html, "https://publisher.example/resources")

        self.assertEqual(
            [link.original_url for link in links],
            [
                "https://merchant.example/product?tag=owner-20",
                "https://tools.example/pricing",
            ],
        )
        self.assertEqual(links[0].source_context, "Recommended camera")

    def test_caps_number_of_links(self) -> None:
        html = "<main>" + "".join(
            f'<a href="https://merchant{i}.example/item">Item {i}</a>' for i in range(5)
        ) + "</main>"

        links = extract_content_links(html, "https://publisher.example/resources", max_links=2)

        self.assertEqual(len(links), 2)


class CollectPublicPageLinksTests(unittest.TestCase):
    def test_rejects_page_disallowed_by_robots(self) -> None:
        routes = {
            "/robots.txt": (200, {"Content-Type": "text/plain"}, b"User-agent: *\nDisallow: /private\n"),
            "/private": (200, {"Content-Type": "text/html"}, b'<main><a href="https://merchant.example/item">Item</a></main>'),
        }

        with FixtureServer(routes) as server:
            with self.assertRaises(RobotsDeniedError):
                collect_public_page_links(f"{server.base_url}/private")

    def test_fetches_allowed_public_page(self) -> None:
        routes = {
            "/robots.txt": (200, {"Content-Type": "text/plain"}, b"User-agent: *\nAllow: /\n"),
            "/resources": (
                200,
                {"Content-Type": "text/html"},
                b'<main><a href="https://merchant.example/item">Item</a></main>',
            ),
        }

        with FixtureServer(routes) as server:
            links = collect_public_page_links(f"{server.base_url}/resources")

        self.assertEqual(len(links), 1)
        self.assertEqual(links[0].source_context, "Item")


if __name__ == "__main__":
    unittest.main()
