from __future__ import annotations

import errno
import json
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .checker import CheckerConfig, check_url
from .document import extract_document_links
from .models import InputValidationError
from .repair import RepairAction, build_repair_pack, render_repair_markdown
from .workflow import Checker, EvidenceRow, check_samples


MAX_BODY_BYTES = 2_000_000


def create_dropzone_server(
    address: tuple[str, int],
    *,
    checker: Checker | None = None,
) -> ThreadingHTTPServer:
    active_checker = checker or _default_checker

    class DropzoneHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path != "/":
                self._send_error(HTTPStatus.NOT_FOUND, "not found")
                return
            self._send_text(HTTPStatus.OK, _INDEX_HTML, content_type="text/html; charset=utf-8")

        def do_POST(self) -> None:
            if self.path != "/api/analyze":
                self._send_error(HTTPStatus.NOT_FOUND, "not found")
                return
            try:
                payload = self._read_json_body()
                result = analyze_payload(payload, checker=active_checker)
            except InputValidationError as error:
                self._send_error(HTTPStatus.BAD_REQUEST, str(error))
                return
            self._send_json(HTTPStatus.OK, result)

        def log_message(self, format: str, *args: object) -> None:
            return

        def _read_json_body(self) -> dict[str, object]:
            length = int(self.headers.get("Content-Length", "0") or "0")
            if length <= 0:
                raise InputValidationError("request body is required")
            if length > MAX_BODY_BYTES:
                raise InputValidationError("request body is too large")
            raw = self.rfile.read(length)
            try:
                payload = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError as error:
                raise InputValidationError("request body must be valid JSON") from error
            if not isinstance(payload, dict):
                raise InputValidationError("request body must be a JSON object")
            return payload

        def _send_json(self, status: HTTPStatus, payload: dict[str, object]) -> None:
            body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
            self.send_response(status.value)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_text(self, status: HTTPStatus, text: str, *, content_type: str) -> None:
            body = text.encode("utf-8")
            self.send_response(status.value)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_error(self, status: HTTPStatus, message: str) -> None:
            self._send_json(status, {"error": message})

    return ThreadingHTTPServer(address, DropzoneHandler)


def create_dropzone_server_with_fallback(
    host: str,
    port: int,
    *,
    attempts: int = 20,
) -> ThreadingHTTPServer:
    if attempts < 1:
        raise InputValidationError("attempts must be at least 1")
    last_error: OSError | None = None
    for offset in range(attempts):
        candidate_port = port + offset if port else 0
        try:
            return create_dropzone_server((host, candidate_port))
        except OSError as error:
            if error.errno != errno.EADDRINUSE or not port:
                raise
            last_error = error
    if last_error:
        raise last_error
    raise InputValidationError("could not start dropzone server")


def dropzone_url(host: str, server: ThreadingHTTPServer) -> str:
    display_host = "127.0.0.1" if host in {"", "0.0.0.0"} else host
    return f"http://{display_host}:{server.server_port}/"


def analyze_payload(payload: dict[str, object], *, checker: Checker | None = None) -> dict[str, object]:
    filename = str(payload.get("filename", "")).strip()
    text = str(payload.get("text", ""))
    if not filename:
        raise InputValidationError("filename is required")
    if not text.strip():
        raise InputValidationError("text is required")
    active_checker = checker or _default_checker
    samples = extract_document_links(text, filename=filename)
    rows = check_samples(samples, checker=active_checker)
    actions = build_repair_pack(rows)
    return {
        "filename": filename,
        "sample_count": len(samples),
        "candidate_issues": sum(1 for row in rows if row.automated_verdict == "candidate_issue"),
        "blocked_or_ambiguous": sum(1 for row in rows if row.blocked_or_ambiguous),
        "ok": sum(1 for row in rows if row.automated_verdict == "ok"),
        "actions": [_action_payload(action) for action in actions],
        "evidence": [_evidence_payload(row) for row in rows],
        "repair_markdown": render_repair_markdown(actions),
    }


def run_dropzone(host: str, port: int, *, open_browser: bool = True) -> None:
    server = create_dropzone_server_with_fallback(host, port)
    url = dropzone_url(host, server)
    print(f"dropzone running at {url}")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def _default_checker(url: str):
    return check_url(url, CheckerConfig())


def _action_payload(action: RepairAction) -> dict[str, object]:
    return {
        "sample_id": action.sample_id,
        "action": action.action,
        "source_context": action.source_context,
        "original_url": action.original_url,
        "final_url": action.final_url,
        "replacement_url": action.replacement_url,
        "editor_instruction": action.editor_instruction,
        "confidence": action.confidence,
        "evidence": action.evidence,
    }


def _evidence_payload(row: EvidenceRow) -> dict[str, Any]:
    return {
        "sample_id": row.sample_id,
        "source_context": row.source_context,
        "original_url": row.original_url,
        "final_url": row.final_url,
        "observed_status": row.observed_status,
        "candidate_issue_type": row.candidate_issue_type,
        "automated_verdict": row.automated_verdict,
        "blocked_or_ambiguous": row.blocked_or_ambiguous,
        "evidence_note": row.evidence_note,
    }


_INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Revenue Link Repair Pack</title>
  <style>
    :root { color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    body { margin: 0; background: #f7f8fb; color: #17202a; }
    main { max-width: 920px; margin: 0 auto; padding: 32px 20px 48px; }
    h1 { font-size: 28px; line-height: 1.15; margin: 0 0 8px; letter-spacing: 0; }
    p { margin: 0 0 16px; color: #435363; }
    #drop { border: 2px dashed #8da2b8; background: #fff; min-height: 180px; display: grid; place-items: center; border-radius: 8px; padding: 24px; text-align: center; }
    #drop.active { border-color: #2357d8; background: #eef3ff; }
    button { border: 0; border-radius: 6px; background: #2357d8; color: #fff; padding: 10px 14px; font: inherit; cursor: pointer; }
    input { display: none; }
    pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #101820; color: #f5f7fb; padding: 16px; border-radius: 8px; }
    .stats { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; margin: 18px 0; }
    .stat { background: #fff; border: 1px solid #dbe2ea; border-radius: 8px; padding: 12px; }
    .stat strong { display: block; font-size: 22px; }
  </style>
</head>
<body>
  <main>
    <h1>Revenue Link Repair Pack</h1>
    <p>Drop a local Markdown or HTML file. Analysis runs on this machine; the file is not uploaded to a remote service.</p>
    <div id="drop">
      <div>
        <p><strong>Drop file here</strong></p>
        <button id="pick" type="button">Choose file</button>
        <input id="file" type="file" accept=".md,.markdown,.html,.htm,text/markdown,text/html">
      </div>
    </div>
    <div class="stats" id="stats" hidden></div>
    <pre id="output">Waiting for a file.</pre>
  </main>
  <script>
    const drop = document.getElementById('drop');
    const fileInput = document.getElementById('file');
    const output = document.getElementById('output');
    const stats = document.getElementById('stats');
    document.getElementById('pick').addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', () => fileInput.files[0] && analyze(fileInput.files[0]));
    drop.addEventListener('dragover', event => { event.preventDefault(); drop.classList.add('active'); });
    drop.addEventListener('dragleave', () => drop.classList.remove('active'));
    drop.addEventListener('drop', event => {
      event.preventDefault();
      drop.classList.remove('active');
      const file = event.dataTransfer.files[0];
      if (file) analyze(file);
    });
    async function analyze(file) {
      output.textContent = 'Analyzing ' + file.name + '...';
      const text = await file.text();
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: file.name, text })
      });
      const payload = await response.json();
      if (!response.ok) {
        output.textContent = payload.error || 'Analysis failed.';
        return;
      }
      stats.hidden = false;
      stats.innerHTML = [
        ['Links', payload.sample_count],
        ['Issues', payload.candidate_issues],
        ['Ambiguous', payload.blocked_or_ambiguous],
        ['OK', payload.ok]
      ].map(([label, value]) => `<div class="stat"><strong>${value}</strong>${label}</div>`).join('');
      output.textContent = payload.repair_markdown;
    }
  </script>
</body>
</html>
"""
