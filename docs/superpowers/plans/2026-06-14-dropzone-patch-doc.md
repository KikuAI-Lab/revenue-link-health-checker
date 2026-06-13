# Dropzone Patch Doc Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a local-first document workflow where a user can drop a Markdown/HTML file, extract links, run checks from their machine, and optionally patch the document from verified replacement actions.

**Architecture:** Keep deterministic document logic in small Python modules, then wrap it with CLI commands and a localhost dropzone server. The browser UI is a thin local client; checking and patching happen in Python so browser CORS does not break link health analysis.

**Tech Stack:** Python 3.11 standard library, existing `unittest` suite, existing `linkhealth` CLI, no new runtime dependencies.

---

### Task 1: Document Link Extraction

**Files:**
- Create: `linkhealth/document.py`
- Test: `tests/test_document.py`

- [ ] **Step 1: Write the failing test**

```python
def test_extracts_markdown_and_html_links_as_samples(self) -> None:
    text = '[Camera](https://shop.example/camera) <a href="https://tools.example/app">Tool</a>'
    samples = extract_document_links(text, filename="roundup.md")
    self.assertEqual([sample.original_url for sample in samples], [
        "https://shop.example/camera",
        "https://tools.example/app",
    ])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_document -v`
Expected: FAIL because `linkhealth.document` does not exist.

- [ ] **Step 3: Write minimal implementation**

Create `extract_document_links(text, filename, lane="web_affiliate")` using `html.parser.HTMLParser` for `<a href>` links and a small Markdown inline-link regex. Return existing `SampleInput` objects with deterministic `sample_id` values.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_document -v`
Expected: PASS.

### Task 2: Safe Document Patching

**Files:**
- Modify: `linkhealth/document.py`
- Test: `tests/test_document.py`

- [ ] **Step 1: Write the failing test**

```python
def test_patches_only_replace_with_url_actions(self) -> None:
    text = '[Camera](https://shop.example/old) [Tool](https://tools.example/keep)'
    actions = [
        RepairAction(... action="replace_with_url", original_url="https://shop.example/old", replacement_url="https://shop.example/new", ...),
        RepairAction(... action="keep", original_url="https://tools.example/keep", replacement_url="", ...),
    ]
    patched = patch_document(text, actions)
    self.assertIn("https://shop.example/new", patched.text)
    self.assertIn("https://tools.example/keep", patched.text)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_document -v`
Expected: FAIL because `patch_document` does not exist.

- [ ] **Step 3: Write minimal implementation**

Add `PatchResult` and `patch_document(text, actions)` that replaces exact URL strings only for `replace_with_url` actions with a non-empty replacement URL. Track replacements, skipped actions, and unchanged links.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_document -v`
Expected: PASS.

### Task 3: CLI Commands

**Files:**
- Modify: `linkhealth/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI tests**

Add tests for:
- `extract-doc-links --input-doc page.md --output-csv samples.csv`
- `patch-doc --input-doc page.md --repair-actions repair-plan.csv --output-doc fixed.md --summary-json patch-summary.json`

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_cli.CliTests.test_extract_doc_links_writes_samples tests.test_cli.CliTests.test_patch_doc_writes_fixed_file -v`
Expected: FAIL because commands do not exist.

- [ ] **Step 3: Write minimal CLI implementation**

Wire the document functions into `argparse` subcommands. Reuse existing CSV writers and repair action readers.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_cli -v`
Expected: PASS.

### Task 4: Local Dropzone Server

**Files:**
- Create: `linkhealth/dropzone.py`
- Modify: `linkhealth/cli.py`
- Test: `tests/test_dropzone.py`

- [ ] **Step 1: Write failing API tests**

Use the stdlib HTTP server in a test thread. POST JSON with `filename` and `text` to `/api/analyze`; expect JSON containing `sample_count`, `actions`, and downloadable Markdown content.

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_dropzone -v`
Expected: FAIL because `linkhealth.dropzone` does not exist.

- [ ] **Step 3: Write minimal dropzone implementation**

Serve a local HTML page at `/` and JSON endpoints under `/api/analyze`. Keep the UI dependency-free and explicit that files stay local.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_dropzone -v`
Expected: PASS.

### Task 5: Docs And Verification

**Files:**
- Modify: `README.md`
- Modify: `.agent/tasks/dropzone-patch-doc/*`

- [ ] **Step 1: Update README**

Document the one-window target:

```bash
linkhealth dropzone
```

Also document the CLI fallback:

```bash
linkhealth extract-doc-links --input-doc page.md --output-csv samples.csv
linkhealth patch-doc --input-doc page.md --repair-actions repair-plan.csv --output-doc fixed.md --summary-json patch-summary.json
```

- [ ] **Step 2: Run full verification**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/demo.py --output-dir .local/demo-output
python3 -m linkhealth --help
git diff --check
```

Expected: all tests pass, demo writes outputs, CLI help lists new commands, diff check clean.
