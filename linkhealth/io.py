from __future__ import annotations

import csv
import json
from collections.abc import Iterable
from pathlib import Path

from .models import InputValidationError, SampleInput

SAMPLE_FIELDS = (
    "sample_id",
    "lane",
    "consent_basis",
    "source_reference",
    "source_context",
    "original_url",
)


def load_samples(path: Path) -> list[SampleInput]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return _load_csv(path)
    if suffix in {".jsonl", ".ndjson"}:
        return _load_jsonl(path)
    raise InputValidationError(f"unsupported sample file format: {path.suffix}")


def _load_csv(path: Path) -> list[SampleInput]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [
            SampleInput.from_mapping(row, row_number)
            for row_number, row in enumerate(reader, start=2)
        ]


def _load_jsonl(path: Path) -> list[SampleInput]:
    samples: list[SampleInput] = []
    with path.open(encoding="utf-8") as handle:
        for row_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise InputValidationError(f"row {row_number}: invalid JSON") from error
            if not isinstance(row, dict):
                raise InputValidationError(f"row {row_number}: expected a JSON object")
            samples.append(SampleInput.from_mapping(row, row_number))
    return samples


def write_samples_csv(path: Path, samples: Iterable[SampleInput]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SAMPLE_FIELDS)
        writer.writeheader()
        for sample in samples:
            writer.writerow(
                {
                    "sample_id": sample.sample_id,
                    "lane": sample.lane,
                    "consent_basis": sample.consent_basis,
                    "source_reference": sample.source_reference,
                    "source_context": sample.source_context,
                    "original_url": sample.original_url,
                }
            )
