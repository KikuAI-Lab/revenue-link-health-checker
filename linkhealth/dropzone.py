from __future__ import annotations

import errno
import json
import webbrowser
from dataclasses import replace
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlsplit

from .checker import CheckerConfig, check_url
from .document import extract_document_links, patch_document
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
            if self.path not in {"/api/analyze", "/api/patch"}:
                self._send_error(HTTPStatus.NOT_FOUND, "not found")
                return
            try:
                payload = self._read_json_body()
                if self.path == "/api/analyze":
                    result = analyze_payload(payload, checker=active_checker)
                else:
                    result = patch_payload(payload, checker=active_checker)
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
    filename, text = _payload_document(payload)
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


def patch_payload(payload: dict[str, object], *, checker: Checker | None = None) -> dict[str, object]:
    filename, text = _payload_document(payload)
    replacements = _payload_replacements(payload)
    active_checker = checker or _default_checker
    rows = check_samples(extract_document_links(text, filename=filename), checker=active_checker)
    actions = _inline_replacement_actions(build_repair_pack(rows), replacements)
    result = patch_document(text, actions)
    return {
        "filename": filename,
        "replacements_applied": result.replacements_applied,
        "skipped_actions": result.skipped_actions,
        "patched_text": result.text,
        "actions": [_action_payload(action) for action in actions],
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


def _payload_document(payload: dict[str, object]) -> tuple[str, str]:
    filename = str(payload.get("filename", "")).strip()
    text = str(payload.get("text", ""))
    if not filename:
        raise InputValidationError("filename is required")
    if not text.strip():
        raise InputValidationError("text is required")
    return filename, text


def _payload_replacements(payload: dict[str, object]) -> dict[str, str]:
    raw = payload.get("replacements", {})
    if not isinstance(raw, dict):
        raise InputValidationError("replacements must be a JSON object")
    replacements: dict[str, str] = {}
    for sample_id, replacement_url in raw.items():
        key = str(sample_id).strip()
        value = str(replacement_url).strip()
        if not key or not value:
            continue
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise InputValidationError(f"replacement URL for {key} must be an absolute http(s) URL")
        replacements[key] = value
    return replacements


def _inline_replacement_actions(
    actions: list[RepairAction],
    replacements: dict[str, str],
) -> list[RepairAction]:
    updated: list[RepairAction] = []
    for action in actions:
        replacement_url = replacements.get(action.sample_id, "")
        if not replacement_url:
            updated.append(action)
            continue
        updated.append(
            replace(
                action,
                action="replace_with_url",
                replacement_url=replacement_url,
                editor_instruction=(
                    f"Replace {action.original_url} with {replacement_url}. "
                    "This replacement was supplied in the local dropzone."
                ),
            )
        )
    return updated


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
    button.secondary { background: #2f455c; }
    button:disabled { background: #9aa8b6; cursor: not-allowed; }
    #file { display: none; }
    input[type="url"] { box-sizing: border-box; width: 100%; border: 1px solid #c8d2dc; border-radius: 6px; padding: 8px 10px; font: inherit; }
    pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #101820; color: #f5f7fb; padding: 16px; border-radius: 8px; }
    .stats { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; margin: 18px 0; }
    .stat { background: #fff; border: 1px solid #dbe2ea; border-radius: 8px; padding: 12px; }
    .stat strong { display: block; font-size: 22px; }
    .panel { margin-top: 18px; }
    .actions { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; }
    table { width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #dbe2ea; border-radius: 8px; overflow: hidden; }
    th, td { border-bottom: 1px solid #e5ebf1; padding: 10px; text-align: left; vertical-align: top; }
    th { background: #eef2f6; color: #243447; font-size: 13px; }
    tr:last-child td { border-bottom: 0; }
    code { overflow-wrap: anywhere; }
    .muted { color: #657384; }
    .downloads { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin: 12px 0; }
    .download { background: #146c43; border-radius: 6px; color: #fff; display: inline-block; padding: 10px 14px; text-decoration: none; }
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
    <section class="panel" id="findings" hidden>
      <div class="actions">
        <button id="apply" type="button">Apply replacements</button>
        <button class="secondary" id="clear" type="button">Clear replacements</button>
      </div>
      <table>
        <thead>
          <tr>
            <th>Action</th>
            <th>Context</th>
            <th>Original URL</th>
            <th>Replacement URL</th>
          </tr>
        </thead>
        <tbody id="rows"></tbody>
      </table>
    </section>
    <section class="panel" id="patched" hidden>
      <div class="downloads">
        <a class="download" id="download" download="patched-document.txt" href="#">Download patched file</a>
        <span class="muted" id="patch-summary"></span>
      </div>
      <pre id="patched-output"></pre>
    </section>
    <pre id="output">Waiting for a file.</pre>
  </main>
  <script>
    const drop = document.getElementById('drop');
    const fileInput = document.getElementById('file');
    const output = document.getElementById('output');
    const stats = document.getElementById('stats');
    const findings = document.getElementById('findings');
    const rows = document.getElementById('rows');
    const patched = document.getElementById('patched');
    const patchedOutput = document.getElementById('patched-output');
    const patchSummary = document.getElementById('patch-summary');
    const download = document.getElementById('download');
    const apply = document.getElementById('apply');
    const clear = document.getElementById('clear');
    let currentFile = null;
    document.getElementById('pick').addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', () => fileInput.files[0] && analyze(fileInput.files[0]));
    apply.addEventListener('click', applyReplacements);
    clear.addEventListener('click', () => {
      rows.querySelectorAll('input[type="url"]').forEach(input => { input.value = ''; });
    });
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
      currentFile = { filename: file.name, text };
      findings.hidden = true;
      patched.hidden = true;
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
      renderActions(payload.actions);
    }
    function renderActions(actions) {
      rows.innerHTML = actions.map(action => {
        const canReplace = action.action !== 'keep';
        const input = canReplace
          ? `<input type="url" data-sample-id="${escapeHtml(action.sample_id)}" placeholder="https://replacement.example/item">`
          : '<span class="muted">No replacement needed</span>';
        return `<tr>
          <td><code>${escapeHtml(action.action)}</code></td>
          <td>${escapeHtml(action.source_context)}</td>
          <td><code>${escapeHtml(action.original_url)}</code></td>
          <td>${input}</td>
        </tr>`;
      }).join('');
      findings.hidden = actions.length === 0;
    }
    async function applyReplacements() {
      if (!currentFile) return;
      const replacements = {};
      rows.querySelectorAll('input[type="url"]').forEach(input => {
        const value = input.value.trim();
        if (value) replacements[input.dataset.sampleId] = value;
      });
      apply.disabled = true;
      output.textContent = 'Applying replacements...';
      const response = await fetch('/api/patch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...currentFile, replacements })
      });
      const payload = await response.json();
      apply.disabled = false;
      if (!response.ok) {
        output.textContent = payload.error || 'Patch failed.';
        return;
      }
      output.textContent = 'Patch ready.';
      patched.hidden = false;
      patchedOutput.textContent = payload.patched_text;
      patchSummary.textContent = `${payload.replacements_applied} replacements applied, ${payload.skipped_actions} skipped.`;
      download.href = URL.createObjectURL(new Blob([payload.patched_text], { type: 'text/plain' }));
      download.download = patchedName(currentFile.filename);
    }
    function patchedName(filename) {
      const index = filename.lastIndexOf('.');
      if (index <= 0) return filename + '.patched.txt';
      return filename.slice(0, index) + '.patched' + filename.slice(index);
    }
    function escapeHtml(value) {
      return String(value).replace(/[&<>"']/g, character => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
      }[character]));
    }
  </script>
</body>
</html>
"""
