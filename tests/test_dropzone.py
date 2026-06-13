from __future__ import annotations

import json
import socket
import unittest
from threading import Thread
from urllib.request import Request, urlopen

from linkhealth.dropzone import create_dropzone_server, create_dropzone_server_with_fallback, dropzone_url
from tests.support import FixtureServer


class DropzoneServerTests(unittest.TestCase):
    def test_formats_reachable_loopback_url(self) -> None:
        server = create_dropzone_server(("127.0.0.1", 0))
        try:
            self.assertEqual(
                dropzone_url("127.0.0.1", server),
                f"http://127.0.0.1:{server.server_port}/",
            )
        finally:
            server.server_close()

    def test_falls_back_when_requested_port_is_busy(self) -> None:
        blocker = socket.socket()
        blocker.bind(("127.0.0.1", 0))
        blocker.listen(1)
        busy_port = blocker.getsockname()[1]
        try:
            server = create_dropzone_server_with_fallback("127.0.0.1", busy_port, attempts=3)
            try:
                self.assertNotEqual(server.server_port, busy_port)
            finally:
                server.server_close()
        finally:
            blocker.close()

    def test_serves_local_page(self) -> None:
        server = create_dropzone_server(("127.0.0.1", 0))
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            body = _get_jsonless(f"http://127.0.0.1:{server.server_port}/")
        finally:
            server.shutdown()
            thread.join(timeout=2)
            server.server_close()

        self.assertIn("Revenue Link Repair Pack", body)
        self.assertIn("Drop", body)

    def test_analyzes_dropped_document_in_same_window_payload(self) -> None:
        routes = {
            "/missing": (404, {}, b"missing"),
            "/ok": (200, {}, b"ok"),
        }
        with FixtureServer(routes) as fixture:
            server = create_dropzone_server(("127.0.0.1", 0))
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                payload = {
                    "filename": "roundup.md",
                    "text": (
                        f"[Missing]({fixture.base_url}/missing)\n"
                        f"[Working]({fixture.base_url}/ok)\n"
                    ),
                }
                response = _post_json(f"http://127.0.0.1:{server.server_port}/api/analyze", payload)
            finally:
                server.shutdown()
                thread.join(timeout=2)
                server.server_close()

        self.assertEqual(response["sample_count"], 2)
        self.assertEqual(response["candidate_issues"], 1)
        self.assertEqual(response["blocked_or_ambiguous"], 0)
        self.assertIn("needs_manual_qa", [action["action"] for action in response["actions"]])
        self.assertIn("# Revenue Link Repair Pack", response["repair_markdown"])


def _post_json(url: str, payload: dict[str, str]) -> dict[str, object]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=10) as response:
        body = response.read().decode("utf-8")
    decoded = json.loads(body)
    if not isinstance(decoded, dict):
        raise AssertionError("expected JSON object response")
    return decoded


def _get_jsonless(url: str) -> str:
    with urlopen(url, timeout=10) as response:
        return response.read().decode("utf-8")


if __name__ == "__main__":
    unittest.main()
