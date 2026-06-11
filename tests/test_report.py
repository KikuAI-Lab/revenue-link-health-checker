from __future__ import annotations

import unittest

from linkhealth.report import Gates, build_report, render_markdown
from linkhealth.workflow import EvidenceRow


class LaneReportTests(unittest.TestCase):
    def test_selects_one_qualifying_lane(self) -> None:
        rows = [
            self._row("tg-1", "telegram_aliexpress", qa="confirmed", issue="http_404", clarity=5),
            self._row("tg-2", "telegram_aliexpress"),
            self._row("web-1", "web_affiliate"),
            self._row("web-2", "web_affiliate"),
        ]

        report = build_report(rows, Gates(min_links=2, min_confirmed_issues=1))

        self.assertEqual(report.verdict, "select_p1a_telegram")
        self.assertEqual(report.lanes["telegram_aliexpress"].confirmed_issues, 1)

    def test_selects_only_one_lane_when_both_pass(self) -> None:
        rows = [
            self._row("tg-1", "telegram_aliexpress", qa="confirmed", issue="http_404", clarity=4),
            self._row("tg-2", "telegram_aliexpress"),
            self._row("web-1", "web_affiliate", qa="confirmed", issue="http_404", clarity=5),
            self._row("web-2", "web_affiliate", qa="confirmed", issue="http_410", clarity=5),
        ]

        report = build_report(rows, Gates(min_links=2, min_confirmed_issues=1))

        self.assertEqual(report.verdict, "select_p1b_web")

    def test_returns_reshape_for_incomplete_benchmark(self) -> None:
        report = build_report(
            [self._row("web-1", "web_affiliate", qa="confirmed", issue="http_404", clarity=5)]
        )

        self.assertEqual(report.verdict, "reshape")
        self.assertIn("fewer than 100 checked links", report.reasons[0])

    def test_does_not_select_lane_until_both_lane_samples_are_complete(self) -> None:
        rows = [
            self._row("web-1", "web_affiliate", qa="confirmed", issue="http_404", clarity=5),
            self._row("web-2", "web_affiliate"),
        ]

        report = build_report(rows, Gates(min_links=2, min_confirmed_issues=1))

        self.assertEqual(report.verdict, "reshape")

    def test_renders_markdown_with_lane_metrics(self) -> None:
        rows = [
            self._row("web-1", "web_affiliate", qa="confirmed", issue="http_404", clarity=5),
            self._row("web-2", "web_affiliate", ambiguous=True),
        ]

        markdown = render_markdown(build_report(rows, Gates(min_links=2, min_confirmed_issues=1)))

        self.assertIn("# Revenue Link Health Lane Comparison", markdown)
        self.assertIn("web_affiliate", markdown)
        self.assertIn("blocked_or_ambiguous_rate", markdown)

    def _row(
        self,
        sample_id: str,
        lane: str,
        *,
        qa: str = "",
        issue: str = "",
        clarity: int = 0,
        ambiguous: bool = False,
    ) -> EvidenceRow:
        verdict = "blocked_or_ambiguous" if ambiguous else ("candidate_issue" if issue else "ok")
        return EvidenceRow(
            sample_id=sample_id,
            lane=lane,
            consent_basis="admin_export" if lane == "telegram_aliexpress" else "public_page",
            source_reference="source",
            source_context="context",
            original_url=f"https://example.com/{sample_id}",
            normalized_url=f"https://example.com/{sample_id}",
            redirect_chain=(f"https://example.com/{sample_id}",),
            final_url=f"https://example.com/{sample_id}",
            observed_status="HTTP 403" if ambiguous else ("HTTP 404" if issue else "HTTP 200"),
            candidate_issue_type=issue,
            automated_verdict=verdict,
            manual_qa_verdict=qa,
            confidence="high" if qa else "",
            false_positive=False,
            blocked_or_ambiguous=ambiguous,
            check_time_seconds=0.01,
            estimated_direct_cost_usd=0.0,
            evidence_note="note",
            checked_at="2026-06-01T00:00:00+00:00",
            review_minutes=0.5 if qa else 0.0,
            value_clarity_score=clarity,
        )


if __name__ == "__main__":
    unittest.main()
