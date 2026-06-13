from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from linkhealth.repair import build_repair_pack, load_replacements, write_repair_pack_files
from linkhealth.workflow import EvidenceRow


class RepairPackTests(unittest.TestCase):
    def test_builds_editor_actions_from_reviewed_evidence(self) -> None:
        rows = [
            self._row(
                "web-001",
                automated_verdict="candidate_issue",
                manual_qa_verdict="confirmed",
                candidate_issue_type="http_404",
                recommended_action="Replace the missing destination.",
            ),
            self._row(
                "web-002",
                automated_verdict="blocked_or_ambiguous",
                blocked_or_ambiguous=True,
                observed_status="HTTP 403",
            ),
            self._row("web-003", automated_verdict="ok"),
        ]

        actions = build_repair_pack(rows, replacements={"web-001": "https://merchant.example/new"})

        self.assertEqual(actions[0].action, "replace_with_url")
        self.assertEqual(actions[0].replacement_url, "https://merchant.example/new")
        self.assertIn("Replace", actions[0].editor_instruction)
        self.assertIn("HTTP 404", actions[0].evidence)
        self.assertEqual(actions[1].action, "manual_review")
        self.assertIn("Do not edit automatically", actions[1].editor_instruction)
        self.assertEqual(actions[2].action, "keep")

    def test_writes_csv_json_and_markdown_repair_pack(self) -> None:
        directory = Path(tempfile.mkdtemp())
        actions = build_repair_pack(
            [
                self._row(
                    "web-001",
                    automated_verdict="candidate_issue",
                    manual_qa_verdict="confirmed",
                    candidate_issue_type="http_404",
                )
            ]
        )

        write_repair_pack_files(
            actions,
            csv_path=directory / "repair-plan.csv",
            json_path=directory / "repair-plan.json",
            markdown_path=directory / "repair-plan.md",
        )

        self.assertIn("remove_or_replace", (directory / "repair-plan.csv").read_text(encoding="utf-8"))
        self.assertEqual(
            json.loads((directory / "repair-plan.json").read_text(encoding="utf-8"))[0]["action"],
            "remove_or_replace",
        )
        self.assertIn("## web-001", (directory / "repair-plan.md").read_text(encoding="utf-8"))

    def test_loads_replacements_csv(self) -> None:
        path = Path(tempfile.mkdtemp()) / "replacements.csv"
        path.write_text(
            "sample_id,replacement_url\n"
            "web-001,https://merchant.example/new\n",
            encoding="utf-8",
        )

        self.assertEqual(load_replacements(path), {"web-001": "https://merchant.example/new"})

    def _row(
        self,
        sample_id: str,
        *,
        automated_verdict: str,
        manual_qa_verdict: str = "",
        candidate_issue_type: str = "",
        recommended_action: str = "",
        blocked_or_ambiguous: bool = False,
        observed_status: str = "HTTP 404",
    ) -> EvidenceRow:
        return EvidenceRow(
            sample_id=sample_id,
            lane="web_affiliate",
            consent_basis="public_page",
            source_reference="https://publisher.example/resources",
            source_context="Recommended product",
            original_url=f"https://merchant.example/{sample_id}",
            normalized_url=f"https://merchant.example/{sample_id}",
            redirect_chain=(f"https://merchant.example/{sample_id}",),
            final_url=f"https://merchant.example/{sample_id}",
            observed_status=observed_status,
            candidate_issue_type=candidate_issue_type,
            automated_verdict=automated_verdict,
            manual_qa_verdict=manual_qa_verdict,
            confidence="high" if manual_qa_verdict == "confirmed" else "",
            false_positive=False,
            blocked_or_ambiguous=blocked_or_ambiguous,
            check_time_seconds=0.01,
            estimated_direct_cost_usd=0.0,
            evidence_note="HTTP status evidence",
            checked_at="2026-06-13T00:00:00+00:00",
            review_minutes=1.0 if manual_qa_verdict == "confirmed" else 0.0,
            value_clarity_score=5 if manual_qa_verdict == "confirmed" else 0,
            recommended_action=recommended_action,
            screenshot_or_evidence_path="evidence/web-001.png" if manual_qa_verdict == "confirmed" else "",
        )


if __name__ == "__main__":
    unittest.main()
