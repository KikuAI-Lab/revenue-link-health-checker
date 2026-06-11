from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .models import InputValidationError, REQUIRED_SAMPLE_FIELDS


PROSPECT_LIST_FIELDS = (
    "domain",
    "candidate_pages",
    "prospect_type",
    "contact_url_or_email",
    "notes",
    "suppression_status",
    "payment_link",
)

QA_DECISION_FIELDS = (
    "sample_id",
    "manual_qa_verdict",
    "confidence",
    "false_positive",
    "review_minutes",
    "value_clarity_score",
    "recommended_action",
    "screenshot_or_evidence_path",
)

METRICS_LOG_FIELDS = (
    "event_id",
    "event_type",
    "lane",
    "count",
    "links_checked",
    "verified_issues",
    "false_positives",
    "blocked_or_ambiguous",
    "review_minutes",
    "messages_sent",
    "replies",
    "payment_clicks",
    "payments",
    "complaints",
    "opt_outs",
    "notes",
    "logged_at",
)


@dataclass(frozen=True)
class BenchmarkKit:
    run_dir: Path
    files: tuple[Path, ...]


def default_benchmark_dir(today: date | None = None) -> Path:
    effective_date = today or date.today()
    return Path(".local") / f"benchmark-{effective_date.isoformat()}"


def init_benchmark_kit(run_dir: Path | None = None, *, force: bool = False) -> BenchmarkKit:
    target_dir = run_dir or default_benchmark_dir()
    templates = _template_payloads(target_dir)
    existing = [path for path in templates if path.exists()]
    if existing and not force:
        names = ", ".join(path.name for path in existing)
        raise InputValidationError(f"benchmark template files already exist: {names}; use --force to overwrite")

    target_dir.mkdir(parents=True, exist_ok=True)
    for path, payload in templates.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(payload, tuple):
            _write_csv_header(path, payload)
        else:
            path.write_text(payload, encoding="utf-8")
    return BenchmarkKit(run_dir=target_dir, files=tuple(templates))


def _template_payloads(run_dir: Path) -> dict[Path, tuple[str, ...] | str]:
    return {
        run_dir / "prospect-list.csv": PROSPECT_LIST_FIELDS,
        run_dir / "samples.csv": REQUIRED_SAMPLE_FIELDS,
        run_dir / "qa-decisions.csv": QA_DECISION_FIELDS,
        run_dir / "metrics-log.csv": METRICS_LOG_FIELDS,
        run_dir / "manual-qa-checklist.md": _manual_qa_checklist(),
        run_dir / "README.md": _run_readme(),
    }


def _write_csv_header(path: Path, fields: tuple[str, ...]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(fields)


def _manual_qa_checklist() -> str:
    return """# Manual QA Checklist

No preview, report, digest, or message is sendable until a human verifies every item below.

## Candidate Issue Review

- Confirm the source page context is public, relevant, and commercial/recommendation-related.
- Confirm the target URL is the visible destination being recommended.
- Confirm redirect/status evidence, including final URL and observed status.
- Confirm the issue type is accurate and not a blocked, rate-limited, CAPTCHA, login, or geo-dependent result.
- Confirm screenshot or evidence path is stored when the issue is commercially meaningful.
- Confirm the recommended action is specific and conservative.

## Before Any Preview Or Outreach

- Confirm non-spam wording: no scare claims, no inflated loss estimate, no attachment, no urgency pressure.
- Confirm contact or channel use is opt-in or manually approved for a tiny experiment.
- Confirm opt-out/suppression status before any manual web message.
- Confirm no AI output is used as final proof of a broken link.
"""


def _run_readme() -> str:
    return """# Revenue Link Health Benchmark Run

This directory is for one real P0 benchmark run. Do not add fake rows to the templates.

## Files

- `prospect-list.csv`: optional prospect/source planning list.
- `samples.csv`: `100` opt-in Telegram/AliExpress links plus `100` public web affiliate/recommendation links.
- `qa-decisions.csv`: human review decisions for candidate issues.
- `metrics-log.csv`: manual sprint events and acquisition/payment signals.
- `manual-qa-checklist.md`: required review gate before any preview, report, digest, or message.

Both lanes need 100 rights-clean checked links per lane before lane selection.

## Commands

Run deterministic checks:

```bash
python3 -m linkhealth check \\
  --input samples.csv \\
  --output-csv evidence.csv \\
  --output-jsonl evidence.jsonl
```

Apply explicit human QA:

```bash
python3 -m linkhealth apply-qa \\
  --evidence evidence.csv \\
  --decisions qa-decisions.csv \\
  --output-csv reviewed-evidence.csv \\
  --output-jsonl reviewed-evidence.jsonl
```

Generate the lane-comparison report:

```bash
python3 -m linkhealth report \\
  --evidence reviewed-evidence.csv \\
  --output-json report.json \\
  --output-markdown report.md \\
  --output-html report.html
```

## Boundaries

- Public Telegram scraping is out of bounds.
- Proxy rotation, browser-identity spoofing, CAPTCHA solving, and rate-limit evasion are out of bounds.
- AI must not confirm broken/unavailable issues.
- Blocked, rate-limited, CAPTCHA, login, timeout, and geo-dependent results remain ambiguous.
- No preview is sendable unless a human verifies the page context, target URL, redirect/status evidence, issue type, and non-spam wording.
"""
