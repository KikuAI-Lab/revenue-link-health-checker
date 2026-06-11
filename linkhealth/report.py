from __future__ import annotations

import html
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from .workflow import EvidenceRow


LANE_VERDICTS = {
    "telegram_aliexpress": "select_p1a_telegram",
    "web_affiliate": "select_p1b_web",
}


@dataclass(frozen=True)
class Gates:
    min_links: int = 100
    min_confirmed_issues: int = 5
    max_false_positive_rate: float = 0.20
    max_blocked_rate: float = 0.20
    max_direct_cost_per_100_usd: float = 5.0
    max_qa_minutes_per_100: float = 60.0
    min_value_clarity_score: float = 4.0


@dataclass(frozen=True)
class LaneMetrics:
    lane: str
    links_checked: int
    candidate_issues: int
    confirmed_issues: int
    confirmed_issues_per_100_links: float
    false_positive_count: int
    candidate_false_positive_rate: float
    blocked_or_ambiguous_count: int
    blocked_or_ambiguous_rate: float
    direct_cost_usd: float
    direct_cost_per_100_links_usd: float
    qa_minutes: float
    qa_minutes_per_100_links: float
    value_clarity_score: float
    passes_gates: bool


@dataclass(frozen=True)
class ComparisonReport:
    generated_at: str
    verdict: str
    reasons: tuple[str, ...]
    lanes: dict[str, LaneMetrics]
    gates: Gates


def build_report(rows: list[EvidenceRow], gates: Gates | None = None) -> ComparisonReport:
    effective_gates = gates or Gates()
    lanes = {
        lane: _lane_metrics(lane, [row for row in rows if row.lane == lane], effective_gates)
        for lane in LANE_VERDICTS
    }
    eligible = [metrics for metrics in lanes.values() if metrics.passes_gates]
    reasons: list[str] = []

    for metrics in lanes.values():
        if metrics.links_checked < effective_gates.min_links:
            reasons.append(
                f"{metrics.lane}: fewer than {effective_gates.min_links} checked links "
                f"({metrics.links_checked})"
            )

    benchmark_complete = all(
        metrics.links_checked >= effective_gates.min_links for metrics in lanes.values()
    )
    if not benchmark_complete:
        verdict = "reshape"
        reasons.append("Benchmark is incomplete; collect more rights-clean rows before lane selection")
    elif eligible:
        selected = max(eligible, key=_ranking_key)
        verdict = LANE_VERDICTS[selected.lane]
        reasons.append(f"{selected.lane}: selected as the strongest lane passing all gates")
    else:
        verdict = "kill"
        reasons.append("No lane passed the P0 quality and economics gates")

    return ComparisonReport(
        generated_at=datetime.now(UTC).isoformat(),
        verdict=verdict,
        reasons=tuple(reasons),
        lanes=lanes,
        gates=effective_gates,
    )


def render_markdown(report: ComparisonReport) -> str:
    lines = [
        "# Revenue Link Health Lane Comparison",
        "",
        f"Generated: `{report.generated_at}`",
        f"Verdict: `{report.verdict}`",
        "",
        "## Lane Metrics",
        "",
        "| lane | links_checked | confirmed_issues | confirmed_per_100 | candidate_false_positive_rate | blocked_or_ambiguous_rate | direct_cost_per_100_usd | qa_minutes_per_100 | value_clarity_score | passes_gates |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for lane in sorted(report.lanes):
        metrics = report.lanes[lane]
        lines.append(
            f"| {metrics.lane} | {metrics.links_checked} | {metrics.confirmed_issues} | "
            f"{metrics.confirmed_issues_per_100_links:.2f} | "
            f"{metrics.candidate_false_positive_rate:.2%} | "
            f"{metrics.blocked_or_ambiguous_rate:.2%} | "
            f"${metrics.direct_cost_per_100_links_usd:.2f} | "
            f"{metrics.qa_minutes_per_100_links:.2f} | "
            f"{metrics.value_clarity_score:.2f} | "
            f"{'yes' if metrics.passes_gates else 'no'} |"
        )
    lines.extend(["", "## Reasons", ""])
    lines.extend(f"- {reason}" for reason in report.reasons)
    return "\n".join(lines) + "\n"


def render_html(report: ComparisonReport) -> str:
    markdown = render_markdown(report)
    return (
        "<!doctype html>\n"
        '<html lang="en"><head><meta charset="utf-8">'
        "<title>Revenue Link Health Lane Comparison</title></head>"
        f"<body><pre>{html.escape(markdown)}</pre></body></html>\n"
    )


def write_report_files(
    report: ComparisonReport,
    *,
    json_path: Path,
    markdown_path: Path,
    html_path: Path,
) -> None:
    for path in (json_path, markdown_path, html_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(_report_payload(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    html_path.write_text(render_html(report), encoding="utf-8")


def _lane_metrics(lane: str, rows: list[EvidenceRow], gates: Gates) -> LaneMetrics:
    links_checked = len(rows)
    candidates = [row for row in rows if row.automated_verdict == "candidate_issue"]
    confirmed = [row for row in rows if row.manual_qa_verdict == "confirmed"]
    false_positives = [row for row in candidates if row.false_positive]
    blocked = [row for row in rows if row.blocked_or_ambiguous]
    direct_cost = sum(row.estimated_direct_cost_usd for row in rows)
    qa_minutes = sum(row.review_minutes for row in rows)
    clarity_values = [row.value_clarity_score for row in rows if row.value_clarity_score]

    metrics = LaneMetrics(
        lane=lane,
        links_checked=links_checked,
        candidate_issues=len(candidates),
        confirmed_issues=len(confirmed),
        confirmed_issues_per_100_links=_per_100(len(confirmed), links_checked),
        false_positive_count=len(false_positives),
        candidate_false_positive_rate=_rate(len(false_positives), len(candidates)),
        blocked_or_ambiguous_count=len(blocked),
        blocked_or_ambiguous_rate=_rate(len(blocked), links_checked),
        direct_cost_usd=round(direct_cost, 6),
        direct_cost_per_100_links_usd=_per_100(direct_cost, links_checked),
        qa_minutes=round(qa_minutes, 4),
        qa_minutes_per_100_links=_per_100(qa_minutes, links_checked),
        value_clarity_score=round(sum(clarity_values) / len(clarity_values), 4)
        if clarity_values
        else 0.0,
        passes_gates=False,
    )
    return LaneMetrics(
        **{
            **asdict(metrics),
            "passes_gates": (
                metrics.links_checked >= gates.min_links
                and metrics.confirmed_issues >= gates.min_confirmed_issues
                and metrics.candidate_false_positive_rate <= gates.max_false_positive_rate
                and metrics.blocked_or_ambiguous_rate <= gates.max_blocked_rate
                and metrics.direct_cost_per_100_links_usd < gates.max_direct_cost_per_100_usd
                and metrics.qa_minutes_per_100_links < gates.max_qa_minutes_per_100
                and metrics.value_clarity_score >= gates.min_value_clarity_score
            ),
        }
    )


def _ranking_key(metrics: LaneMetrics) -> tuple[float, float, float, float, float, float]:
    return (
        metrics.confirmed_issues_per_100_links,
        metrics.value_clarity_score,
        -metrics.candidate_false_positive_rate,
        -metrics.blocked_or_ambiguous_rate,
        -metrics.qa_minutes_per_100_links,
        -metrics.direct_cost_per_100_links_usd,
    )


def _per_100(value: float, count: int) -> float:
    return round((value * 100 / count) if count else 0.0, 4)


def _rate(value: int, count: int) -> float:
    return round((value / count) if count else 0.0, 6)


def _report_payload(report: ComparisonReport) -> dict[str, object]:
    return {
        "generated_at": report.generated_at,
        "verdict": report.verdict,
        "reasons": list(report.reasons),
        "gates": asdict(report.gates),
        "lanes": {lane: asdict(metrics) for lane, metrics in report.lanes.items()},
    }
