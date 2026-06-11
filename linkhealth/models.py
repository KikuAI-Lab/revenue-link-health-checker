from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
from urllib.parse import urlsplit


SUPPORTED_LANES = {"telegram_aliexpress", "web_affiliate"}
REQUIRED_SAMPLE_FIELDS = (
    "sample_id",
    "lane",
    "consent_basis",
    "source_reference",
    "source_context",
    "original_url",
)


class InputValidationError(ValueError):
    """Raised when an operator-provided input row violates the P0 contract."""


@dataclass(frozen=True)
class SampleInput:
    sample_id: str
    lane: str
    consent_basis: str
    source_reference: str
    source_context: str
    original_url: str

    @classmethod
    def from_mapping(cls, row: Mapping[str, object], row_number: int) -> "SampleInput":
        values: dict[str, str] = {}
        for field in REQUIRED_SAMPLE_FIELDS:
            value = row.get(field)
            if value is None:
                raise InputValidationError(f"row {row_number}: missing required field {field}")
            values[field] = str(value).strip()

        if not values["sample_id"]:
            raise InputValidationError(f"row {row_number}: sample_id is required")
        if values["lane"] not in SUPPORTED_LANES:
            raise InputValidationError(f"row {row_number}: unsupported lane {values['lane']!r}")
        if not values["source_reference"]:
            raise InputValidationError(f"row {row_number}: source_reference is required")
        if values["lane"] == "telegram_aliexpress" and not values["consent_basis"]:
            raise InputValidationError(
                f"row {row_number}: telegram_aliexpress rows require consent_basis"
            )

        parsed = urlsplit(values["original_url"])
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise InputValidationError(
                f"row {row_number}: original_url must be an absolute http(s) URL"
            )

        return cls(**values)
