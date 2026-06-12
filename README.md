# Revenue Link Health Checker

Standalone local-first tooling for monetized, affiliate, and recommendation-link health checks.

The project helps an operator turn user-provided or rights-clean public link samples into a QA-ready report. It can identify deterministic candidate issues, preserve redirect/status evidence, apply manual review decisions, and generate Markdown, HTML, JSON, CSV, and JSONL outputs.

It is intentionally not a SaaS dashboard, browser extension, WordPress plugin, outreach system, public Telegram scraper, crawler fleet, or automatic link replacement tool.

## What It Does

- imports CSV or JSONL link samples;
- optionally collects outbound content links from one robots-allowed public page;
- checks redirects, HTTP status, timeout, access-control, and ambiguous outcomes;
- keeps blocked, CAPTCHA-like, login-gated, geo-dependent, and rate-limited results as ambiguous;
- requires manual QA before a candidate issue becomes a confirmed issue;
- generates a compact report for proof batches and small operator workflows.

## Privacy And Safety

- No API keys are required.
- No AI model is required.
- No account or backend service is required.
- Your local files are not uploaded by this tool.
- The `check` and `collect-web` commands make outbound HTTP requests from your machine.
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

The demo starts a loopback HTTP fixture server, checks synthetic links, applies manual QA decisions, and writes a complete local report bundle.

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
  report.md
  report.html
  report.json
```

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

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Status

MVP. The current version is best treated as an operator CLI and proof workflow. Any paid report, monitoring, API, MCP server, or automated replacement workflow should wait for stronger usage and validation evidence.
