from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlsplit

from .models import InputValidationError
from .workflow import EvidenceRow


REPAIR_ACTION_FIELDS = (
    "sample_id",
    "action",
    "source_reference",
    "source_context",
    "original_url",
    "final_url",
    "replacement_url",
    "editor_instruction",
    "confidence",
    "evidence",
    "screenshot_or_evidence_path",
)


@dataclass(frozen=True)
class RepairAction:
    sample_id: str
    action: str
    source_reference: str
    source_context: str
    original_url: str
    final_url: str
    replacement_url: str
    editor_instruction: str
    confidence: str
    evidence: str
    screenshot_or_evidence_path: str


def build_repair_pack(
    rows: list[EvidenceRow],
    replacements: dict[str, str] | None = None,
) -> list[RepairAction]:
    replacement_by_id = replacements or {}
    return [_repair_action(row, replacement_by_id.get(row.sample_id, "")) for row in rows]


def load_replacements(path: Path) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8") as handle:
        replacements: dict[str, str] = {}
        for row_number, row in enumerate(csv.DictReader(handle), start=2):
            sample_id = str(row.get("sample_id", "")).strip()
            replacement_url = str(row.get("replacement_url", "")).strip()
            if not sample_id:
                raise InputValidationError(f"row {row_number}: sample_id is required")
            if not replacement_url:
                raise InputValidationError(f"row {row_number}: replacement_url is required")
            if sample_id in replacements:
                raise InputValidationError(f"row {row_number}: duplicate replacement for {sample_id}")
            parsed = urlsplit(replacement_url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise InputValidationError(
                    f"row {row_number}: replacement_url must be an absolute http(s) URL"
                )
            replacements[sample_id] = replacement_url
    return replacements


def write_repair_pack_files(
    actions: list[RepairAction],
    *,
    csv_path: Path,
    json_path: Path,
    markdown_path: Path,
) -> None:
    for path in (csv_path, json_path, markdown_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    _write_repair_csv(csv_path, actions)
    json_path.write_text(
        json.dumps([asdict(action) for action in actions], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(render_repair_markdown(actions), encoding="utf-8")


def render_repair_markdown(actions: list[RepairAction]) -> str:
    lines = ["# Revenue Link Repair Pack", ""]
    for action in actions:
        lines.extend(
            [
                f"## {action.sample_id}",
                "",
                f"- Action: `{action.action}`",
                f"- Source: {action.source_reference}",
                f"- Context: {action.source_context}",
                f"- Original URL: {action.original_url}",
                f"- Final URL: {action.final_url}",
                f"- Replacement URL: {action.replacement_url or '[none supplied]'}",
                f"- Confidence: {action.confidence or '[not reviewed]'}",
                f"- Evidence: {action.evidence}",
                "",
                action.editor_instruction,
                "",
            ]
        )
    return "\n".join(lines)


def _repair_action(row: EvidenceRow, replacement_url: str) -> RepairAction:
    action = _action(row, replacement_url)
    return RepairAction(
        sample_id=row.sample_id,
        action=action,
        source_reference=row.source_reference,
        source_context=row.source_context,
        original_url=row.original_url,
        final_url=row.final_url,
        replacement_url=replacement_url,
        editor_instruction=_editor_instruction(row, action, replacement_url),
        confidence=row.confidence,
        evidence=_evidence(row),
        screenshot_or_evidence_path=row.screenshot_or_evidence_path,
    )


def _action(row: EvidenceRow, replacement_url: str) -> str:
    if row.manual_qa_verdict == "confirmed":
        return "replace_with_url" if replacement_url else "remove_or_replace"
    if row.blocked_or_ambiguous:
        return "manual_review"
    if row.automated_verdict == "candidate_issue":
        return "needs_manual_qa"
    return "keep"


def _editor_instruction(row: EvidenceRow, action: str, replacement_url: str) -> str:
    if action == "replace_with_url":
        return (
            f"Replace {row.original_url} with {replacement_url}. "
            "Keep the surrounding copy only if the replacement still matches the recommendation."
        )
    if action == "remove_or_replace":
        return row.recommended_action or (
            "Replace this destination with a current equivalent or remove the recommendation."
        )
    if action == "manual_review":
        return "Do not edit automatically. Recheck the page in a browser and decide manually."
    if action == "needs_manual_qa":
        return "Review this candidate issue before editing the source page."
    return "Keep this link unchanged."


def _evidence(row: EvidenceRow) -> str:
    parts = [row.observed_status]
    if row.candidate_issue_type:
        parts.append(row.candidate_issue_type)
    if row.evidence_note:
        parts.append(row.evidence_note)
    return " | ".join(parts)


def _write_repair_csv(path: Path, actions: list[RepairAction]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=REPAIR_ACTION_FIELDS)
        writer.writeheader()
        for action in actions:
            writer.writerow(asdict(action))
