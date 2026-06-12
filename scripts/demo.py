from __future__ import annotations

import argparse
import csv
import json
import sys
from contextlib import AbstractContextManager
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from typing import ClassVar

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from linkhealth.io import write_samples_csv
from linkhealth.models import SampleInput
from linkhealth.report import Gates, build_report, write_report_files
from linkhealth.workflow import (
    QADecision,
    apply_qa_decisions,
    check_samples,
    write_evidence_csv,
    write_evidence_jsonl,
)


class _DemoHandler(BaseHTTPRequestHandler):
    routes: ClassVar[dict[str, tuple[int, dict[str, str], bytes]]] = {
        "/ok": (200, {"Content-Type": "text/plain"}, b"ok"),
        "/missing": (404, {"Content-Type": "text/plain"}, b"missing"),
        "/gone": (410, {"Content-Type": "text/plain"}, b"gone"),
        "/blocked": (403, {"Content-Type": "text/plain"}, b"forbidden"),
        "/redirect": (302, {"Location": "/ok"}, b""),
    }

    def do_GET(self) -> None:
        status, headers, body = self.routes.get(
            self.path,
            (404, {"Content-Type": "text/plain"}, b"missing"),
        )
        self.send_response(status)
        for name, value in headers.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


class _DemoServer(AbstractContextManager["_DemoServer"]):
    def __init__(self) -> None:
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _DemoHandler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)

    @property
    def base_url(self) -> str:
        host, port = self.server.server_address
        return f"http://{host}:{port}"

    def __enter__(self) -> "_DemoServer":
        self.thread.start()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.server.shutdown()
        self.thread.join(timeout=2)
        self.server.server_close()


def run_demo(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    with _DemoServer() as server:
        samples = _samples(server.base_url)
        rows = check_samples(samples)

    write_samples_csv(output_dir / "samples.csv", samples)
    write_evidence_csv(output_dir / "evidence.csv", rows)
    write_evidence_jsonl(output_dir / "evidence.jsonl", rows)

    decisions = _decisions()
    _write_decisions(output_dir / "qa-decisions.csv", decisions)
    reviewed = apply_qa_decisions(rows, decisions)
    write_evidence_csv(output_dir / "reviewed-evidence.csv", reviewed)
    write_evidence_jsonl(output_dir / "reviewed-evidence.jsonl", reviewed)

    report = build_report(
        reviewed,
        Gates(
            min_links=5,
            min_confirmed_issues=1,
        ),
    )
    write_report_files(
        report,
        json_path=output_dir / "report.json",
        markdown_path=output_dir / "report.md",
        html_path=output_dir / "report.html",
    )
    return {
        "verdict": report.verdict,
        "links_checked": len(rows),
        "output_dir": str(output_dir),
    }


def _samples(base_url: str) -> list[SampleInput]:
    definitions = (
        ("tg-001", "telegram_aliexpress", "admin_export_demo", "approved-channel-demo", "post 1", "/missing"),
        ("tg-002", "telegram_aliexpress", "admin_export_demo", "approved-channel-demo", "post 2", "/ok"),
        ("tg-003", "telegram_aliexpress", "admin_export_demo", "approved-channel-demo", "post 3", "/blocked"),
        ("tg-004", "telegram_aliexpress", "admin_export_demo", "approved-channel-demo", "post 4", "/redirect"),
        ("tg-005", "telegram_aliexpress", "admin_export_demo", "approved-channel-demo", "post 5", "/ok"),
        ("web-001", "web_affiliate", "public_page", "https://publisher.example/resources", "Missing camera", "/missing"),
        ("web-002", "web_affiliate", "public_page", "https://publisher.example/resources", "Gone tool", "/gone"),
        ("web-003", "web_affiliate", "public_page", "https://publisher.example/resources", "Redirected tool", "/redirect"),
        ("web-004", "web_affiliate", "public_page", "https://publisher.example/resources", "Working tool", "/ok"),
        ("web-005", "web_affiliate", "public_page", "https://publisher.example/resources", "Working camera", "/ok"),
    )
    return [
        SampleInput(
            sample_id=sample_id,
            lane=lane,
            consent_basis=consent_basis,
            source_reference=source_reference,
            source_context=source_context,
            original_url=f"{base_url}{path}",
        )
        for sample_id, lane, consent_basis, source_reference, source_context, path in definitions
    ]


def _decisions() -> list[QADecision]:
    return [
        QADecision(
            sample_id="tg-001",
            manual_qa_verdict="confirmed",
            confidence="high",
            review_minutes=0.5,
            value_clarity_score=4,
            recommended_action="Replace or remove the unavailable offer.",
        ),
        QADecision(
            sample_id="web-001",
            manual_qa_verdict="confirmed",
            confidence="high",
            review_minutes=0.5,
            value_clarity_score=5,
            recommended_action="Replace or remove the missing destination.",
        ),
        QADecision(
            sample_id="web-002",
            manual_qa_verdict="confirmed",
            confidence="high",
            review_minutes=0.5,
            value_clarity_score=5,
            recommended_action="Replace or remove the gone destination.",
        ),
    ]


def _write_decisions(path: Path, decisions: list[QADecision]) -> None:
    fieldnames = list(asdict(decisions[0]))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for decision in decisions:
            writer.writerow(asdict(decision))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path(".local/demo-output"))
    args = parser.parse_args()
    print(json.dumps(run_demo(args.output_dir), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
