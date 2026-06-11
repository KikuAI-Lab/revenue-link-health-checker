from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from linkhealth.cli import main


class BenchmarkInitTests(unittest.TestCase):
    def test_benchmark_init_creates_operator_templates(self) -> None:
        directory = Path(tempfile.mkdtemp()) / "benchmark"

        result = main(["benchmark-init", "--run-dir", str(directory)])

        self.assertEqual(result, 0)
        expected_files = {
            "prospect-list.csv",
            "samples.csv",
            "qa-decisions.csv",
            "metrics-log.csv",
            "manual-qa-checklist.md",
            "README.md",
        }
        self.assertEqual({path.name for path in directory.iterdir()}, expected_files)
        self.assertEqual(
            _csv_header(directory / "samples.csv"),
            [
                "sample_id",
                "lane",
                "consent_basis",
                "source_reference",
                "source_context",
                "original_url",
            ],
        )
        self.assertEqual(_csv_rows(directory / "samples.csv"), [])
        self.assertIn("python3 -m linkhealth check", (directory / "README.md").read_text(encoding="utf-8"))
        self.assertIn("100 rights-clean checked links per lane", (directory / "README.md").read_text(encoding="utf-8"))

    def test_benchmark_init_refuses_to_overwrite_without_force(self) -> None:
        directory = Path(tempfile.mkdtemp()) / "benchmark"
        self.assertEqual(main(["benchmark-init", "--run-dir", str(directory)]), 0)
        original = directory / "samples.csv"
        original.write_text("custom\n", encoding="utf-8")

        result = main(["benchmark-init", "--run-dir", str(directory)])

        self.assertEqual(result, 2)
        self.assertEqual(original.read_text(encoding="utf-8"), "custom\n")

    def test_benchmark_init_force_overwrites_generated_templates(self) -> None:
        directory = Path(tempfile.mkdtemp()) / "benchmark"
        self.assertEqual(main(["benchmark-init", "--run-dir", str(directory)]), 0)
        samples = directory / "samples.csv"
        samples.write_text("custom\n", encoding="utf-8")

        result = main(["benchmark-init", "--run-dir", str(directory), "--force"])

        self.assertEqual(result, 0)
        self.assertEqual(_csv_header(samples)[0], "sample_id")

    def test_benchmark_templates_include_prd_contract_fields(self) -> None:
        directory = Path(tempfile.mkdtemp()) / "benchmark"
        self.assertEqual(main(["benchmark-init", "--run-dir", str(directory)]), 0)

        self.assertEqual(
            _csv_header(directory / "prospect-list.csv"),
            [
                "domain",
                "candidate_pages",
                "prospect_type",
                "contact_url_or_email",
                "notes",
                "suppression_status",
                "payment_link",
            ],
        )
        self.assertEqual(
            _csv_header(directory / "qa-decisions.csv"),
            [
                "sample_id",
                "manual_qa_verdict",
                "confidence",
                "false_positive",
                "review_minutes",
                "value_clarity_score",
                "recommended_action",
                "screenshot_or_evidence_path",
            ],
        )
        metrics_header = _csv_header(directory / "metrics-log.csv")
        for field in (
            "verified_issues",
            "false_positives",
            "review_minutes",
            "messages_sent",
            "replies",
            "payment_clicks",
            "payments",
            "complaints",
            "opt_outs",
        ):
            self.assertIn(field, metrics_header)

        checklist = (directory / "manual-qa-checklist.md").read_text(encoding="utf-8")
        for required_phrase in (
            "page context",
            "target URL",
            "redirect/status evidence",
            "issue type",
            "non-spam wording",
        ):
            self.assertIn(required_phrase, checklist)


def _csv_header(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        return next(reader)


def _csv_rows(path: Path) -> list[list[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        next(reader)
        return list(reader)


if __name__ == "__main__":
    unittest.main()
