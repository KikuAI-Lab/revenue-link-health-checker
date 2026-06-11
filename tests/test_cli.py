from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from linkhealth.cli import main
from linkhealth.io import load_samples
from linkhealth.workflow import load_evidence
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


if __name__ == "__main__":
    unittest.main()
