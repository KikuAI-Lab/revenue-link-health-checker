# Revenue Link Health P0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local Python CLI that checks dual-lane monetized-link samples, preserves raw evidence, applies explicit human QA, and emits a single lane-selection verdict.

**Architecture:** A small `linkhealth` package separates data contracts, transport/checking, public web extraction, evidence I/O, report generation, and CLI parsing. Runtime code uses only the Python standard library. Tests run against a loopback HTTP fixture server so redirects, failures, blocks, CAPTCHA-like pages, robots rules, and extraction stay reproducible.

**Tech Stack:** Python 3.14-compatible standard library, `unittest`, CSV, JSONL, `urllib`, `html.parser`.

---

### Task 1: Freeze Contracts And Test Harness

**Files:**
- Create: `pyproject.toml`
- Create: `tests/__init__.py`
- Create: `tests/support.py`
- Create: `tests/test_io.py`

- [ ] Write fixture-server helpers with deterministic routes for `200`, redirects, `404`, `410`, `403`, `429`, `500`, CAPTCHA-like HTML, robots deny, and HTML extraction.
- [ ] Write failing import tests for CSV, JSONL, required fields, and Telegram consent validation.
- [ ] Run `python3 -m unittest tests.test_io -v`; expect missing-module failures.
- [ ] Implement the minimal package metadata, models, and importer.
- [ ] Re-run `python3 -m unittest tests.test_io -v`; expect PASS.

### Task 2: Deterministic Checker

**Files:**
- Create: `tests/test_checker.py`
- Create: `linkhealth/checker.py`

- [ ] Write failing tests for normalization, redirect capture, `404`, persistent `5xx`, redirect loop, redirect cap, `403`, `429`, timeout-like failure, and CAPTCHA-like body.
- [ ] Run `python3 -m unittest tests.test_checker -v`; expect failures because checker functions do not exist.
- [ ] Implement URL normalization and serial bounded checking with one retry by default.
- [ ] Re-run `python3 -m unittest tests.test_checker -v`; expect PASS.

### Task 3: Rights-Clean Web Extraction

**Files:**
- Create: `tests/test_web.py`
- Create: `linkhealth/web.py`

- [ ] Write failing tests for robots denial, content-link extraction, asset/social/internal exclusion, and cap enforcement.
- [ ] Run `python3 -m unittest tests.test_web -v`; expect failures because web functions do not exist.
- [ ] Implement robots-aware public page collection and HTML parsing.
- [ ] Re-run `python3 -m unittest tests.test_web -v`; expect PASS.

### Task 4: Evidence Workflow And Manual QA

**Files:**
- Create: `tests/test_workflow.py`
- Create: `linkhealth/workflow.py`

- [ ] Write failing tests that raw evidence rows are complete, automated checks never confirm issues, QA decisions apply explicitly, and ambiguous rows cannot become confirmed.
- [ ] Run `python3 -m unittest tests.test_workflow -v`; expect failures because workflow functions do not exist.
- [ ] Implement evidence creation, CSV/JSONL writing, and QA-decision application.
- [ ] Re-run `python3 -m unittest tests.test_workflow -v`; expect PASS.

### Task 5: Lane Report And CLI

**Files:**
- Create: `tests/test_report.py`
- Create: `tests/test_cli.py`
- Create: `linkhealth/report.py`
- Create: `linkhealth/cli.py`
- Create: `linkhealth/__main__.py`

- [ ] Write failing tests for lane metrics, gate evaluation, single verdict selection, incomplete benchmark reshape, and CLI output creation.
- [ ] Run `python3 -m unittest tests.test_report tests.test_cli -v`; expect missing-module failures.
- [ ] Implement report generation and `check`, `apply-qa`, `collect-web`, and `report` CLI commands.
- [ ] Re-run `python3 -m unittest tests.test_report tests.test_cli -v`; expect PASS.

### Task 6: Reproducible Demo And Operator Docs

**Files:**
- Create: `scripts/demo.py`
- Create: `README.md`

- [ ] Add a loopback-only demo that creates synthetic dual-lane samples, runs checks, simulates explicit operator QA decisions, and writes all report artifacts.
- [ ] Document boundaries and commands in README.
- [ ] Run `python3 scripts/demo.py --output-dir .local/demo-output`; expect generated evidence and report paths.
- [ ] Run `python3 -m unittest discover -s tests -v`; expect all tests PASS.

### Task 7: Proof Pack

**Files:**
- Create: `.agent/tasks/revenue-link-health-p0/evidence.md`
- Create: `.agent/tasks/revenue-link-health-p0/evidence.json`
- Create: `.agent/tasks/revenue-link-health-p0/verdict.json`

- [ ] Capture fresh full-test and demo output under `.agent/tasks/revenue-link-health-p0/raw/`.
- [ ] Audit AC1-AC7 against current files and command output.
- [ ] Write evidence files and fresh verifier verdict.
- [ ] Run a final `git status --short` and confirm `.omx/` is ignored.
