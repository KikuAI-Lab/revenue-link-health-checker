# Revenue Link Repair Pack

Standalone local-first tooling for monetized, affiliate, and recommendation-link repair packs.

The project helps a user drop a local Markdown/HTML page or an operator sample file into a deterministic repair workflow. It can identify deterministic candidate issues, preserve redirect/status evidence, apply manual review decisions, accept optional replacement URLs, patch exact document URLs, and generate editor-ready actions instead of only saying "you have broken links."

It is intentionally not a SaaS dashboard, browser extension, WordPress plugin, outreach system, public Telegram scraper, crawler fleet, or automatic link replacement tool.

## What It Does

- imports CSV or JSONL link samples;
- extracts links from local Markdown and HTML documents;
- extracts plain-text HTTP(S) links from local notes, CSV-like exports, and pasted text files;
- runs an offline deterministic diagnosis mode for local document problems that do not require live HTTP status checks;
- optionally collects outbound content links from one robots-allowed public page;
- checks redirects, HTTP status, timeout, access-control, and ambiguous outcomes;
- keeps blocked, CAPTCHA-like, login-gated, geo-dependent, and rate-limited results as ambiguous;
- requires manual QA before a candidate issue becomes a confirmed issue;
- generates repair-pack CSV, JSON, and Markdown outputs for editor workflows;
- patches local Markdown/HTML documents from verified replacement actions;
- runs a dependency-free localhost dropzone UI for one-window document analysis and patching;
- generates compact benchmark reports for proof batches.

## Privacy And Safety

- No API keys are required.
- No AI model is required.
- No account or backend service is required.
- Your local files are not uploaded by this tool.
- The `check`, `collect-web`, and `dropzone` analysis flows make outbound HTTP requests from your machine.
- The tool does not bypass access controls, rotate proxies, solve CAPTCHAs, spoof browser identity, or scrape private/authenticated pages.

## Install

Python 3.11 or newer is required.

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e .
```

Then run:

```bash
linkhealth --help
```

You can also run the module directly:

```bash
python3 -m linkhealth --help
```

## Offline Demo

The demo starts a loopback HTTP fixture server, checks synthetic links, applies manual QA decisions, and writes a complete local repair/report bundle.

```bash
python3 scripts/demo.py --output-dir .local/demo-output
```

Expected files:

```text
.local/demo-output/
  samples.csv
  evidence.csv
  evidence.jsonl
  qa-decisions.csv
  reviewed-evidence.csv
  reviewed-evidence.jsonl
  repair-plan.csv
  repair-plan.json
  repair-plan.md
  report.md
  report.html
  report.json
```

## Sample Files

Synthetic sample files live in [examples/](examples/). Use them to try the dropzone or document extraction without customer data.

```bash
python3 -m linkhealth extract-doc-links \
  --input-doc examples/sample-affiliate-roundup.txt \
  --output-csv .local/sample-roundup-links.csv
```

## Local Dropzone

For the simplest local workflow, start the dropzone:

```bash
linkhealth dropzone
```

Then open the shown localhost URL and drop a Markdown, HTML, TXT, or CSV-like file. The browser sends the file only to the local Python process on your machine. The result appears in the same window as a compact repair pack with candidate issues, ambiguous results, OK links, editor instructions, replacement URL inputs, patched preview, and patched-file download.

This is not a hosted SaaS upload flow. External links are checked from your machine so browser CORS does not block status and redirect inspection.

The dropzone also includes an **Offline deterministic diagnosis only** mode. That mode does not call external URLs. It can flag local document issues such as unsupported link targets, insecure `http://` destinations, affiliate-looking tracking parameters, and duplicate tracking-parameter variants. It does not prove whether a destination is live, redirected, blocked, or sold out.

## Basic Workflow

Create a CSV sample file:

```csv
sample_id,lane,consent_basis,source_reference,source_context,original_url
web-001,web_affiliate,public_page,https://example.com/resources,Recommended camera,https://merchant.example/product
```

Check links:

```bash
linkhealth check \
  --input samples.csv \
  --output-csv .local/run/evidence.csv \
  --output-jsonl .local/run/evidence.jsonl
```

Apply human QA decisions:

```csv
sample_id,manual_qa_verdict,confidence,false_positive,review_minutes,value_clarity_score,recommended_action,screenshot_or_evidence_path
web-001,confirmed,high,false,1.5,5,Replace or remove the unavailable destination,evidence/web-001.png
```

```bash
linkhealth apply-qa \
  --evidence .local/run/evidence.csv \
  --decisions qa-decisions.csv \
  --output-csv .local/run/reviewed-evidence.csv \
  --output-jsonl .local/run/reviewed-evidence.jsonl
```

Generate reports:

```bash
linkhealth report \
  --evidence .local/run/reviewed-evidence.csv \
  --output-json .local/run/report.json \
  --output-markdown .local/run/report.md \
  --output-html .local/run/report.html
```

Generate an editor-ready repair pack:

```csv
sample_id,replacement_url
web-001,https://merchant.example/current-product
```

```bash
linkhealth repair-pack \
  --evidence .local/run/reviewed-evidence.csv \
  --replacements replacements.csv \
  --output-csv .local/run/repair-plan.csv \
  --output-json .local/run/repair-plan.json \
  --output-markdown .local/run/repair-plan.md
```

Repair-pack actions are:

- `replace_with_url` when a manually confirmed issue has a supplied replacement URL;
- `remove_or_replace` when a manually confirmed issue needs an editor decision;
- `manual_review` when the checker saw a blocked, CAPTCHA-like, login-gated, rate-limited, or geo-dependent result;
- `needs_manual_qa` when an automated candidate issue has not been reviewed yet;
- `keep` when no action is needed.

## Document Workflow

Extract links from a local Markdown, HTML, TXT, or CSV-like file into sample CSV:

```bash
linkhealth extract-doc-links \
  --input-doc page.md \
  --output-csv .local/run/samples.csv
```

Patch exact URLs in a local document after replacements have been manually verified and written into a repair action CSV or JSON file:

```bash
linkhealth patch-doc \
  --input-doc page.md \
  --repair-actions .local/run/repair-plan.csv \
  --output-doc .local/run/page.fixed.md \
  --summary-json .local/run/patch-summary.json
```

`patch-doc` only applies `replace_with_url` actions that include a replacement URL. It does not auto-edit blocked, ambiguous, unreviewed, or remove-or-replace actions.

One-command document analysis and inline replacement patching are available through `linkhealth dropzone`.

For a fully offline first pass, use the dropzone checkbox labeled **Offline deterministic diagnosis only**. This is best when you want a fast local repair surface before any live URL checking. Switch it off when you need HTTP status and redirect evidence from your machine.

## Public Page Collection

Collect external content links from one public robots-allowed page:

```bash
linkhealth collect-web \
  --page-url https://example.com/resources \
  --sample-prefix example-resources \
  --output-csv .local/run/web-samples.csv
```

The collector excludes internal links, common assets, scripts, styles, social destinations, `mailto`, and `tel` links.

## Proof-Batch Gates

Default report gates are conservative:

- at least `100` checked links;
- at least `5` confirmed meaningful issues per `100` links;
- candidate false-positive rate `<=20%`;
- blocked or ambiguous rate `<=20%`;
- direct cost `<$5` per `100` links;
- manual QA `<60` minutes per `100` links;
- value clarity score `>=4/5`.

See [docs/validation.md](docs/validation.md) for the first public web-affiliate proof batch summary.

The next validation lane is documented in [docs/activation-sprint.md](docs/activation-sprint.md) and [docs/proof-batch-2.md](docs/proof-batch-2.md).

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Status

MVP. The current version is a local-first repair workflow with both CLI and localhost dropzone surfaces. Any paid report, monitoring, hosted API, MCP server, or bulk automation should wait for stronger usage and validation evidence.
