from __future__ import annotations

import csv
import json
from collections.abc import Callable, Iterable, Mapping
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from pathlib import Path

from .checker import CheckResult, check_url
from .models import InputValidationError, SampleInput


EVIDENCE_FIELDS = (
    "sample_id",
    "lane",
    "consent_basis",
    "source_reference",
    "source_context",
    "original_url",
    "normalized_url",
    "redirect_chain",
    "final_url",
    "observed_status",
    "candidate_issue_type",
    "automated_verdict",
    "manual_qa_verdict",
    "confidence",
    "false_positive",
    "blocked_or_ambiguous",
    "check_time_seconds",
    "estimated_direct_cost_usd",
    "evidence_note",
    "checked_at",
    "review_minutes",
    "value_clarity_score",
    "recommended_action",
    "screenshot_or_evidence_path",
)


@dataclass(frozen=True)
class EvidenceRow:
    sample_id: str
    lane: str
    consent_basis: str
    source_reference: str
    source_context: str
    original_url: str
    normalized_url: str
    redirect_chain: tuple[str, ...]
    final_url: str
    observed_status: str
    candidate_issue_type: str
    automated_verdict: str
    manual_qa_verdict: str
    confidence: str
    false_positive: bool
    blocked_or_ambiguous: bool
    check_time_seconds: float
    estimated_direct_cost_usd: float
    evidence_note: str
    checked_at: str
    review_minutes: float = 0.0
    value_clarity_score: int = 0
    recommended_action: str = ""
    screenshot_or_evidence_path: str = ""


@dataclass(frozen=True)
class QADecision:
    sample_id: str
    manual_qa_verdict: str
    confidence: str = ""
    false_positive: bool = False
    review_minutes: float = 0.0
    value_clarity_score: int = 0
    recommended_action: str = ""
    screenshot_or_evidence_path: str = ""


Checker = Callable[[str], CheckResult]


def check_samples(
    samples: Iterable[SampleInput],
    *,
    checker: Checker = check_url,
) -> list[EvidenceRow]:
    rows: list[EvidenceRow] = []
    for sample in samples:
        result = checker(sample.original_url)
        rows.append(_evidence_row(sample, result))
    return rows


def write_evidence_csv(path: Path, rows: Iterable[EvidenceRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=EVIDENCE_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(_row_to_mapping(row, jsonl=False))


def write_evidence_jsonl(path: Path, rows: Iterable[EvidenceRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(_row_to_mapping(row, jsonl=True), sort_keys=True) + "\n")


def load_evidence(path: Path) -> list[EvidenceRow]:
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            return [_mapping_to_row(row) for row in csv.DictReader(handle)]
    if path.suffix.lower() in {".jsonl", ".ndjson"}:
        with path.open(encoding="utf-8") as handle:
            return [_mapping_to_row(json.loads(line)) for line in handle if line.strip()]
    raise InputValidationError(f"unsupported evidence file format: {path.suffix}")


def apply_qa_decisions(
    rows: Iterable[EvidenceRow],
    decisions: Iterable[QADecision],
) -> list[EvidenceRow]:
    decisions_by_id: dict[str, QADecision] = {}
    for decision in decisions:
        if decision.sample_id in decisions_by_id:
            raise InputValidationError(f"duplicate QA decision for {decision.sample_id}")
        decisions_by_id[decision.sample_id] = decision

    reviewed: list[EvidenceRow] = []
    seen_ids: set[str] = set()
    for row in rows:
        decision = decisions_by_id.get(row.sample_id)
        if decision is None:
            reviewed.append(row)
            continue
        seen_ids.add(row.sample_id)
        _validate_qa_decision(row, decision)
        reviewed.append(
            replace(
                row,
                manual_qa_verdict=decision.manual_qa_verdict,
                confidence=decision.confidence,
                false_positive=(
                    decision.false_positive
                    or (
                        row.automated_verdict == "candidate_issue"
                        and decision.manual_qa_verdict == "rejected"
                    )
                ),
                review_minutes=decision.review_minutes,
                value_clarity_score=decision.value_clarity_score,
                recommended_action=decision.recommended_action,
                screenshot_or_evidence_path=decision.screenshot_or_evidence_path,
            )
        )

    unknown_ids = sorted(set(decisions_by_id) - seen_ids)
    if unknown_ids:
        raise InputValidationError(f"QA decisions reference unknown sample ids: {', '.join(unknown_ids)}")
    return reviewed


def load_qa_decisions(path: Path) -> list[QADecision]:
    with path.open(newline="", encoding="utf-8") as handle:
        decisions: list[QADecision] = []
        for row_number, row in enumerate(csv.DictReader(handle), start=2):
            sample_id = str(row.get("sample_id", "")).strip()
            verdict = str(row.get("manual_qa_verdict", "")).strip()
            if not sample_id:
                raise InputValidationError(f"row {row_number}: sample_id is required")
            if not verdict:
                raise InputValidationError(f"row {row_number}: manual_qa_verdict is required")
            decisions.append(
                QADecision(
                    sample_id=sample_id,
                    manual_qa_verdict=verdict,
                    confidence=str(row.get("confidence", "")).strip(),
                    false_positive=_bool_value(row.get("false_positive", False)),
                    review_minutes=float(row.get("review_minutes", 0.0) or 0.0),
                    value_clarity_score=int(row.get("value_clarity_score", 0) or 0),
                    recommended_action=str(row.get("recommended_action", "")).strip(),
                    screenshot_or_evidence_path=str(
                        row.get("screenshot_or_evidence_path", "")
                    ).strip(),
                )
            )
    return decisions


def _evidence_row(sample: SampleInput, result: CheckResult) -> EvidenceRow:
    return EvidenceRow(
        sample_id=sample.sample_id,
        lane=sample.lane,
        consent_basis=sample.consent_basis,
        source_reference=sample.source_reference,
        source_context=sample.source_context,
        original_url=sample.original_url,
        normalized_url=result.normalized_url,
        redirect_chain=result.redirect_chain,
        final_url=result.final_url,
        observed_status=result.observed_status,
        candidate_issue_type=result.candidate_issue_type,
        automated_verdict=result.automated_verdict,
        manual_qa_verdict="",
        confidence="",
        false_positive=False,
        blocked_or_ambiguous=result.blocked_or_ambiguous,
        check_time_seconds=result.check_time_seconds,
        estimated_direct_cost_usd=result.estimated_direct_cost_usd,
        evidence_note=result.evidence_note,
        checked_at=datetime.now(UTC).isoformat(),
    )


def _row_to_mapping(row: EvidenceRow, *, jsonl: bool) -> dict[str, object]:
    mapping = asdict(row)
    mapping["redirect_chain"] = list(row.redirect_chain) if jsonl else json.dumps(row.redirect_chain)
    return mapping


def _mapping_to_row(mapping: Mapping[str, object]) -> EvidenceRow:
    redirect_chain_value = mapping.get("redirect_chain", ())
    if isinstance(redirect_chain_value, str):
        redirect_chain_raw = json.loads(redirect_chain_value)
    else:
        redirect_chain_raw = redirect_chain_value
    if not isinstance(redirect_chain_raw, (list, tuple)):
        raise InputValidationError("redirect_chain must be a JSON list")

    return EvidenceRow(
        sample_id=str(mapping.get("sample_id", "")),
        lane=str(mapping.get("lane", "")),
        consent_basis=str(mapping.get("consent_basis", "")),
        source_reference=str(mapping.get("source_reference", "")),
        source_context=str(mapping.get("source_context", "")),
        original_url=str(mapping.get("original_url", "")),
        normalized_url=str(mapping.get("normalized_url", "")),
        redirect_chain=tuple(str(url) for url in redirect_chain_raw),
        final_url=str(mapping.get("final_url", "")),
        observed_status=str(mapping.get("observed_status", "")),
        candidate_issue_type=str(mapping.get("candidate_issue_type", "")),
        automated_verdict=str(mapping.get("automated_verdict", "")),
        manual_qa_verdict=str(mapping.get("manual_qa_verdict", "")),
        confidence=str(mapping.get("confidence", "")),
        false_positive=_bool_value(mapping.get("false_positive", False)),
        blocked_or_ambiguous=_bool_value(mapping.get("blocked_or_ambiguous", False)),
        check_time_seconds=float(mapping.get("check_time_seconds", 0.0)),
        estimated_direct_cost_usd=float(mapping.get("estimated_direct_cost_usd", 0.0)),
        evidence_note=str(mapping.get("evidence_note", "")),
        checked_at=str(mapping.get("checked_at", "")),
        review_minutes=float(mapping.get("review_minutes", 0.0)),
        value_clarity_score=int(mapping.get("value_clarity_score", 0)),
        recommended_action=str(mapping.get("recommended_action", "")),
        screenshot_or_evidence_path=str(mapping.get("screenshot_or_evidence_path", "")),
    )


def _validate_qa_decision(row: EvidenceRow, decision: QADecision) -> None:
    allowed_verdicts = {"confirmed", "rejected", "reviewed_no_issue"}
    if decision.manual_qa_verdict not in allowed_verdicts:
        raise InputValidationError(
            f"unsupported QA verdict {decision.manual_qa_verdict!r} for {decision.sample_id}"
        )
    if decision.manual_qa_verdict == "confirmed" and row.blocked_or_ambiguous:
        raise InputValidationError(f"cannot confirm ambiguous result for {decision.sample_id}")
    if decision.manual_qa_verdict == "confirmed" and row.automated_verdict != "candidate_issue":
        raise InputValidationError(f"cannot confirm non-candidate result for {decision.sample_id}")
    if decision.value_clarity_score not in range(0, 6):
        raise InputValidationError(f"value_clarity_score must be in range 0..5 for {decision.sample_id}")
    if decision.review_minutes < 0:
        raise InputValidationError(f"review_minutes cannot be negative for {decision.sample_id}")


def _bool_value(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}
