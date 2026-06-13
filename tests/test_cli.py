from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from linkhealth.cli import main
from linkhealth.io import load_samples
from linkhealth.workflow import EvidenceRow, load_evidence, write_evidence_csv
from tests.support import FixtureServer


class CliTests(unittest.TestCase):
    def test_check_apply_qa_and_report_workflow(self) -> None:
        directory = Path(tempfile.mkdtemp())
        evidence = directory / "evidence.csv"
        reviewed = directory / "reviewed.csv"
        report_json = directory / "report.json"
        report_md = directory / "report.md"
        report_html = directory / "report.html"
        routes = {
            "/missing": (404, {}, b"missing"),
            "/ok": (200, {}, b"ok"),
        }

        with FixtureServer(routes) as server:
            samples = directory / "samples.csv"
            samples.write_text(
                "sample_id,lane,consent_basis,source_reference,source_context,original_url\n"
                f"web-001,web_affiliate,public_page,source,Missing item,{server.base_url}/missing\n"
                f"web-002,web_affiliate,public_page,source,Working item,{server.base_url}/ok\n"
                f"tg-001,telegram_aliexpress,admin_export_demo,approved-channel,Working offer,{server.base_url}/ok\n"
                f"tg-002,telegram_aliexpress,admin_export_demo,approved-channel,Working offer,{server.base_url}/ok\n",
                encoding="utf-8",
            )
            self.assertEqual(main(["check", "--input", str(samples), "--output-csv", str(evidence)]), 0)

        rows = load_evidence(evidence)
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0].manual_qa_verdict, "")

        decisions = directory / "qa.csv"
        decisions.write_text(
            "sample_id,manual_qa_verdict,confidence,false_positive,review_minutes,"
            "value_clarity_score,recommended_action,screenshot_or_evidence_path\n"
            "web-001,confirmed,high,false,0.5,5,Replace missing destination,evidence/web-001.png\n",
            encoding="utf-8",
        )
        self.assertEqual(
            main(
                [
                    "apply-qa",
                    "--evidence",
                    str(evidence),
                    "--decisions",
                    str(decisions),
                    "--output-csv",
                    str(reviewed),
                ]
            ),
            0,
        )
        self.assertEqual(
            main(
                [
                    "report",
                    "--evidence",
                    str(reviewed),
                    "--output-json",
                    str(report_json),
                    "--output-markdown",
                    str(report_md),
                    "--output-html",
                    str(report_html),
                    "--min-links",
                    "2",
                    "--min-confirmed-issues",
                    "1",
                ]
            ),
            0,
        )

        payload = json.loads(report_json.read_text(encoding="utf-8"))
        self.assertEqual(payload["verdict"], "select_p1b_web")
        self.assertTrue(report_md.exists())
        self.assertTrue(report_html.exists())

    def test_collect_web_writes_sample_csv(self) -> None:
        directory = Path(tempfile.mkdtemp())
        output = directory / "samples.csv"
        routes = {
            "/robots.txt": (200, {}, b"User-agent: *\nAllow: /\n"),
            "/resources": (
                200,
                {"Content-Type": "text/html"},
                b'<main><a href="https://merchant.example/item">Recommended item</a></main>',
            ),
        }

        with FixtureServer(routes) as server:
            result = main(
                [
                    "collect-web",
                    "--page-url",
                    f"{server.base_url}/resources",
                    "--output-csv",
                    str(output),
                    "--sample-prefix",
                    "page-a",
                ]
            )

        self.assertEqual(result, 0)
        samples = load_samples(output)
        self.assertEqual(samples[0].sample_id, "page-a-001")
        self.assertEqual(samples[0].source_context, "Recommended item")

    def test_repair_pack_writes_editor_outputs(self) -> None:
        directory = Path(tempfile.mkdtemp())
        evidence = directory / "reviewed.csv"
        replacements = directory / "replacements.csv"
        output_csv = directory / "repair-plan.csv"
        output_json = directory / "repair-plan.json"
        output_md = directory / "repair-plan.md"
        write_evidence_csv(
            evidence,
            [
                EvidenceRow(
                    sample_id="web-001",
                    lane="web_affiliate",
                    consent_basis="public_page",
                    source_reference="source",
                    source_context="Missing item",
                    original_url="https://old.example/item",
                    normalized_url="https://old.example/item",
                    redirect_chain=("https://old.example/item",),
                    final_url="https://old.example/item",
                    observed_status="HTTP 404",
                    candidate_issue_type="http_404",
                    automated_verdict="candidate_issue",
                    manual_qa_verdict="confirmed",
                    confidence="high",
                    false_positive=False,
                    blocked_or_ambiguous=False,
                    check_time_seconds=0.01,
                    estimated_direct_cost_usd=0,
                    evidence_note="HTTP 404",
                    checked_at="2026-06-13T00:00:00+00:00",
                    review_minutes=1,
                    value_clarity_score=5,
                    recommended_action="Replace missing destination",
                    screenshot_or_evidence_path="evidence/web-001.png",
                )
            ],
        )
        replacements.write_text(
            "sample_id,replacement_url\n"
            "web-001,https://new.example/item\n",
            encoding="utf-8",
        )

        self.assertEqual(
            main(
                [
                    "repair-pack",
                    "--evidence",
                    str(evidence),
                    "--replacements",
                    str(replacements),
                    "--output-csv",
                    str(output_csv),
                    "--output-json",
                    str(output_json),
                    "--output-markdown",
                    str(output_md),
                ]
            ),
            0,
        )

        self.assertIn("replace_with_url", output_csv.read_text(encoding="utf-8"))
        self.assertEqual(json.loads(output_json.read_text(encoding="utf-8"))[0]["replacement_url"], "https://new.example/item")
        self.assertIn("Replace https://old.example/item", output_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
