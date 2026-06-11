from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .benchmark import init_benchmark_kit
from .checker import CheckerConfig, check_url
from .io import load_samples, write_samples_csv
from .models import InputValidationError, SampleInput
from .report import Gates, build_report, write_report_files
from .web import WebCollectionError, collect_public_page_links
from .workflow import (
    apply_qa_decisions,
    check_samples,
    load_evidence,
    load_qa_decisions,
    write_evidence_csv,
    write_evidence_jsonl,
)


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (InputValidationError, WebCollectionError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="linkhealth")
    subparsers = parser.add_subparsers(required=True)

    collect = subparsers.add_parser("collect-web", help="collect public content links from one robots-allowed page")
    collect.add_argument("--page-url", required=True)
    collect.add_argument("--output-csv", type=Path, required=True)
    collect.add_argument("--sample-prefix", default="web")
    collect.add_argument("--max-links", type=int, default=150)
    collect.add_argument("--timeout-seconds", type=float, default=10.0)
    collect.set_defaults(handler=_collect_web)

    benchmark = subparsers.add_parser("benchmark-init", help="create local benchmark run templates")
    benchmark.add_argument("--run-dir", type=Path)
    benchmark.add_argument("--force", action="store_true")
    benchmark.set_defaults(handler=_benchmark_init)

    check = subparsers.add_parser("check", help="check imported dual-lane samples")
    check.add_argument("--input", type=Path, required=True)
    check.add_argument("--output-csv", type=Path, required=True)
    check.add_argument("--output-jsonl", type=Path)
    check.add_argument("--max-redirects", type=int, default=10)
    check.add_argument("--timeout-seconds", type=float, default=10.0)
    check.add_argument("--retries", type=int, default=1)
    check.set_defaults(handler=_check)

    qa = subparsers.add_parser("apply-qa", help="apply explicit operator QA decisions")
    qa.add_argument("--evidence", type=Path, required=True)
    qa.add_argument("--decisions", type=Path, required=True)
    qa.add_argument("--output-csv", type=Path, required=True)
    qa.add_argument("--output-jsonl", type=Path)
    qa.set_defaults(handler=_apply_qa)

    report = subparsers.add_parser("report", help="generate lane-comparison report")
    report.add_argument("--evidence", type=Path, required=True)
    report.add_argument("--output-json", type=Path, required=True)
    report.add_argument("--output-markdown", type=Path, required=True)
    report.add_argument("--output-html", type=Path, required=True)
    report.add_argument("--min-links", type=int, default=100)
    report.add_argument("--min-confirmed-issues", type=int, default=5)
    report.add_argument("--max-false-positive-rate", type=float, default=0.20)
    report.add_argument("--max-blocked-rate", type=float, default=0.20)
    report.add_argument("--max-direct-cost-per-100-usd", type=float, default=5.0)
    report.add_argument("--max-qa-minutes-per-100", type=float, default=60.0)
    report.add_argument("--min-value-clarity-score", type=float, default=4.0)
    report.set_defaults(handler=_report)

    return parser


def _benchmark_init(args: argparse.Namespace) -> int:
    kit = init_benchmark_kit(args.run_dir, force=args.force)
    print(f"created benchmark kit -> {kit.run_dir}")
    return 0


def _collect_web(args: argparse.Namespace) -> int:
    links = collect_public_page_links(
        args.page_url,
        max_links=args.max_links,
        timeout_seconds=args.timeout_seconds,
    )
    samples = [
        SampleInput(
            sample_id=f"{args.sample_prefix}-{index:03d}",
            lane="web_affiliate",
            consent_basis="public_page",
            source_reference=link.source_reference,
            source_context=link.source_context,
            original_url=link.original_url,
        )
        for index, link in enumerate(links, start=1)
    ]
    write_samples_csv(args.output_csv, samples)
    print(f"collected {len(samples)} links -> {args.output_csv}")
    return 0


def _check(args: argparse.Namespace) -> int:
    samples = load_samples(args.input)
    config = CheckerConfig(
        max_redirects=args.max_redirects,
        timeout_seconds=args.timeout_seconds,
        retries=args.retries,
    )
    rows = check_samples(samples, checker=lambda url: check_url(url, config))
    write_evidence_csv(args.output_csv, rows)
    if args.output_jsonl:
        write_evidence_jsonl(args.output_jsonl, rows)
    print(f"checked {len(rows)} links -> {args.output_csv}")
    return 0


def _apply_qa(args: argparse.Namespace) -> int:
    rows = load_evidence(args.evidence)
    decisions = load_qa_decisions(args.decisions)
    reviewed = apply_qa_decisions(rows, decisions)
    write_evidence_csv(args.output_csv, reviewed)
    if args.output_jsonl:
        write_evidence_jsonl(args.output_jsonl, reviewed)
    print(f"applied {len(decisions)} QA decisions -> {args.output_csv}")
    return 0


def _report(args: argparse.Namespace) -> int:
    rows = load_evidence(args.evidence)
    gates = Gates(
        min_links=args.min_links,
        min_confirmed_issues=args.min_confirmed_issues,
        max_false_positive_rate=args.max_false_positive_rate,
        max_blocked_rate=args.max_blocked_rate,
        max_direct_cost_per_100_usd=args.max_direct_cost_per_100_usd,
        max_qa_minutes_per_100=args.max_qa_minutes_per_100,
        min_value_clarity_score=args.min_value_clarity_score,
    )
    report = build_report(rows, gates)
    write_report_files(
        report,
        json_path=args.output_json,
        markdown_path=args.output_markdown,
        html_path=args.output_html,
    )
    print(f"verdict {report.verdict} -> {args.output_markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
