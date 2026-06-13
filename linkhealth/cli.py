from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .benchmark import init_benchmark_kit
from .checker import CheckerConfig, check_url
from .document import extract_document_links, patch_document
from .dropzone import run_dropzone
from .io import load_samples, write_samples_csv
from .models import InputValidationError, SampleInput
from .repair import build_repair_pack, load_repair_actions, load_replacements, write_repair_pack_files
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

    repair = subparsers.add_parser("repair-pack", help="generate editor-ready repair actions from reviewed evidence")
    repair.add_argument("--evidence", type=Path, required=True)
    repair.add_argument("--replacements", type=Path)
    repair.add_argument("--output-csv", type=Path, required=True)
    repair.add_argument("--output-json", type=Path, required=True)
    repair.add_argument("--output-markdown", type=Path, required=True)
    repair.set_defaults(handler=_repair_pack)

    extract_doc = subparsers.add_parser("extract-doc-links", help="extract link samples from a local Markdown or HTML file")
    extract_doc.add_argument("--input-doc", type=Path, required=True)
    extract_doc.add_argument("--output-csv", type=Path, required=True)
    extract_doc.add_argument("--lane", default="web_affiliate")
    extract_doc.set_defaults(handler=_extract_doc_links)

    patch_doc = subparsers.add_parser("patch-doc", help="patch a local document from verified repair actions")
    patch_doc.add_argument("--input-doc", type=Path, required=True)
    patch_doc.add_argument("--repair-actions", type=Path, required=True)
    patch_doc.add_argument("--output-doc", type=Path, required=True)
    patch_doc.add_argument("--summary-json", type=Path, required=True)
    patch_doc.set_defaults(handler=_patch_doc)

    dropzone = subparsers.add_parser("dropzone", help="run a local browser dropzone for document analysis")
    dropzone.add_argument("--host", default="127.0.0.1")
    dropzone.add_argument("--port", type=int, default=8765)
    dropzone.add_argument("--no-open", action="store_true")
    dropzone.set_defaults(handler=_dropzone)

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


def _repair_pack(args: argparse.Namespace) -> int:
    rows = load_evidence(args.evidence)
    replacements = load_replacements(args.replacements) if args.replacements else None
    actions = build_repair_pack(rows, replacements=replacements)
    write_repair_pack_files(
        actions,
        csv_path=args.output_csv,
        json_path=args.output_json,
        markdown_path=args.output_markdown,
    )
    print(f"repair actions {len(actions)} -> {args.output_markdown}")
    return 0


def _extract_doc_links(args: argparse.Namespace) -> int:
    text = args.input_doc.read_text(encoding="utf-8")
    samples = extract_document_links(text, filename=args.input_doc.name, lane=args.lane)
    write_samples_csv(args.output_csv, samples)
    print(f"extracted {len(samples)} links -> {args.output_csv}")
    return 0


def _patch_doc(args: argparse.Namespace) -> int:
    text = args.input_doc.read_text(encoding="utf-8")
    actions = load_repair_actions(args.repair_actions)
    result = patch_document(text, actions)
    args.output_doc.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_doc.write_text(result.text, encoding="utf-8")
    args.summary_json.write_text(
        json.dumps(
            {
                "input_doc": str(args.input_doc),
                "output_doc": str(args.output_doc),
                "repair_actions": len(actions),
                "replacements_applied": result.replacements_applied,
                "skipped_actions": result.skipped_actions,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"patched {result.replacements_applied} links -> {args.output_doc}")
    return 0


def _dropzone(args: argparse.Namespace) -> int:
    try:
        run_dropzone(args.host, args.port, open_browser=not args.no_open)
    except KeyboardInterrupt:
        print("\ndropzone stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
