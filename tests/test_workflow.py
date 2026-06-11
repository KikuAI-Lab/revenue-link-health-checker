from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from linkhealth.checker import CheckResult
from linkhealth.models import InputValidationError, SampleInput
from linkhealth.workflow import (
    QADecision,
    apply_qa_decisions,
    check_samples,
    load_evidence,
    write_evidence_csv,
    write_evidence_jsonl,
)


class EvidenceWorkflowTests(unittest.TestCase):
    def test_check_samples_preserves_raw_fields_without_auto_confirmation(self) -> None:
        sample = self._sample("web-001", "web_affiliate")

        rows = check_samples([sample], checker=self._candidate_checker)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].sample_id, "web-001")
        self.assertEqual(rows[0].normalized_url, "https://merchant.example/missing")
        self.assertEqual(rows[0].candidate_issue_type, "http_404")
        self.assertEqual(rows[0].manual_qa_verdict, "")
        self.assertFalse(rows[0].false_positive)

    def test_writes_and_loads_csv_and_jsonl(self) -> None:
        row = check_samples([self._sample("web-001", "web_affiliate")], checker=self._candidate_checker)[0]
        directory = Path(tempfile.mkdtemp())
        csv_path = directory / "evidence.csv"
        jsonl_path = directory / "evidence.jsonl"

        write_evidence_csv(csv_path, [row])
        write_evidence_jsonl(jsonl_path, [row])

        self.assertEqual(load_evidence(csv_path), [row])
        self.assertEqual(load_evidence(jsonl_path), [row])

    def test_applies_explicit_qa_confirmation_to_candidate(self) -> None:
        row = check_samples([self._sample("web-001", "web_affiliate")], checker=self._candidate_checker)[0]
        decision = QADecision(
            sample_id="web-001",
            manual_qa_verdict="confirmed",
            confidence="high",
            false_positive=False,
            review_minutes=2.5,
            value_clarity_score=5,
            recommended_action="Replace the missing destination.",
            screenshot_or_evidence_path="evidence/web-001.png",
        )

        reviewed = apply_qa_decisions([row], [decision])

        self.assertEqual(reviewed[0].manual_qa_verdict, "confirmed")
        self.assertEqual(reviewed[0].review_minutes, 2.5)
        self.assertEqual(reviewed[0].value_clarity_score, 5)

    def test_rejects_confirmation_of_ambiguous_row(self) -> None:
        row = check_samples([self._sample("tg-001", "telegram_aliexpress")], checker=self._ambiguous_checker)[0]
        decision = QADecision(
            sample_id="tg-001",
            manual_qa_verdict="confirmed",
            confidence="high",
        )

        with self.assertRaisesRegex(InputValidationError, "ambiguous"):
            apply_qa_decisions([row], [decision])

    def test_marks_rejected_candidate_as_false_positive(self) -> None:
        row = check_samples([self._sample("web-001", "web_affiliate")], checker=self._candidate_checker)[0]
        decision = QADecision(
            sample_id="web-001",
            manual_qa_verdict="rejected",
            confidence="low",
        )

        reviewed = apply_qa_decisions([row], [decision])

        self.assertTrue(reviewed[0].false_positive)

    def _sample(self, sample_id: str, lane: str) -> SampleInput:
        return SampleInput(
            sample_id=sample_id,
            lane=lane,
            consent_basis="admin_export" if lane == "telegram_aliexpress" else "public_page",
            source_reference="approved-source",
            source_context="Product row",
            original_url="https://merchant.example/missing",
        )

    def _candidate_checker(self, url: str) -> CheckResult:
        return CheckResult(
            normalized_url=url,
            final_url=url,
            redirect_chain=(url,),
            observed_status="HTTP 404",
            candidate_issue_type="http_404",
            automated_verdict="candidate_issue",
            blocked_or_ambiguous=False,
            evidence_note="HTTP 404 returned by final destination",
            check_time_seconds=0.01,
        )

    def _ambiguous_checker(self, url: str) -> CheckResult:
        return CheckResult(
            normalized_url=url,
            final_url=url,
            redirect_chain=(url,),
            observed_status="HTTP 403",
            candidate_issue_type="",
            automated_verdict="blocked_or_ambiguous",
            blocked_or_ambiguous=True,
            evidence_note="HTTP 403 can indicate access controls",
            check_time_seconds=0.01,
        )


if __name__ == "__main__":
    unittest.main()
