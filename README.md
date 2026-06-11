# Revenue Link Health Checker

Local-first tooling for monetized/recommendation-link risk analysis.

The active public P0 direction is a free KikuAI hub drop-in analyzer:

- user drops or pastes a CSV, HTML, or Markdown file;
- analysis runs locally on the user's machine;
- output is a conservative downloadable risk report;
- no account, upload, backend analysis, live fetch, payment, or AI dependency is required.

The Python CLI in this repository is an operator proof workflow and benchmark harness. It is not the public hub MVP, SaaS product, Telegram bot, crawler fleet, monitoring backend, or outreach system.

See `docs/affiliate-revenue-link-health-mvp-prd.md` for the current free hub drop-in PRD.

The first self-selected public web-affiliate proof batch is documented in
`docs/research-sprint/first-web-affiliate-proof-batch-results.md`. It checked
`100` links and found `3` manually confirmed meaningful issues, so paid-report
testing remains gated on stronger source selection or owner-provided exports.

## Runtime

- Python `3.11+`
- Standard library only
- No API keys
- No AliExpress API dependency
- No AI dependency

## Offline Demo

Run:

```bash
python3 scripts/demo.py --output-dir .local/demo-output
```

The demo starts a loopback HTTP fixture server, checks `10` synthetic links, applies explicit QA decisions, and writes:

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

The demo proves workflow behavior only. It is not market evidence and does not replace the real rights-clean `100 + 100` benchmark.

## Operator Proof Workflow

The CLI remains useful for later rights-clean proof batches, especially when a human operator needs live checks and manual QA outside the browser-only P0.

### 0. Initialize a proof folder

Create headers-only operator templates:

```bash
python3 -m linkhealth benchmark-init --run-dir .local/proof-batch-2026-06-11
```

If `--run-dir` is omitted, the command writes to `.local/benchmark-YYYY-MM-DD`.
It creates:

```text
prospect-list.csv
samples.csv
qa-decisions.csv
metrics-log.csv
manual-qa-checklist.md
README.md
```

Existing template files are not overwritten unless `--force` is passed.

The original benchmark kit supports the older dual-lane `100 + 100` research method. For the current hub-first path, use it as an operator worksheet for a single `100`-link public affiliate/recommendation proof batch unless a later decision reopens the Telegram lane.

### 1. Prepare input

Create a CSV or JSONL file:

```csv
sample_id,lane,consent_basis,source_reference,source_context,original_url
tg-001,telegram_aliexpress,admin_export_2026-06-01,approved-channel-a,"post 481",https://s.click.aliexpress.com/example
web-001,web_affiliate,public_page,https://example.com/resources,"Recommended camera",https://merchant.example/product
```

Every `telegram_aliexpress` row requires an explicit `consent_basis`.

### 2. Check links

```bash
python3 -m linkhealth check \
  --input samples.csv \
  --output-csv .local/run/evidence.csv \
  --output-jsonl .local/run/evidence.jsonl
```

The checker preserves original URLs, query parameters, redirect chains, timestamps, status evidence, and ambiguous outcomes.

### 3. Apply human QA

Review every candidate issue and prepare:

```csv
sample_id,manual_qa_verdict,confidence,false_positive,review_minutes,value_clarity_score,recommended_action,screenshot_or_evidence_path
web-001,confirmed,high,false,1.5,5,Replace the missing destination,evidence/web-001.png
```

Then run:

```bash
python3 -m linkhealth apply-qa \
  --evidence .local/run/evidence.csv \
  --decisions qa-decisions.csv \
  --output-csv .local/run/reviewed-evidence.csv \
  --output-jsonl .local/run/reviewed-evidence.jsonl
```

Blocked, CAPTCHA-like, login-gated, geo-dependent, and rate-limited results cannot be confirmed.

### 4. Generate comparison report

```bash
python3 -m linkhealth report \
  --evidence .local/run/reviewed-evidence.csv \
  --output-json .local/run/report.json \
  --output-markdown .local/run/report.md \
  --output-html .local/run/report.html
```

Default proof-batch gates:

- at least `100` checked links in the selected proof batch;
- at least `5` confirmed meaningful issues per `100` links;
- candidate false-positive rate `<=20%`;
- blocked or ambiguous rate `<=20%`;
- direct cost `<$5` per `100` links;
- manual QA `<60` minutes per `100` links;
- value clarity score `>=4/5`.

Verdict is exactly one of:

```text
select_p1a_telegram
select_p1b_web
reshape
kill
```

## Public Web Collection

Collect external content links from one public robots-allowed page:

```bash
python3 -m linkhealth collect-web \
  --page-url https://example.com/resources \
  --sample-prefix example-resources \
  --output-csv .local/run/web-samples.csv
```

The collector excludes internal links, assets, scripts, styles, navigation containers, social destinations, `mailto`, and `tel`.

## Safety Boundaries

- Public pages only.
- robots.txt checked before public page collection.
- Default checker limits: `10` redirect hops, `10s` timeout, `1` retry, serial processing.
- `403`, `429`, timeout, CAPTCHA-like, login-gated, and geo-dependent results remain ambiguous.
- No public Telegram scraping.
- No proxy rotation, browser-identity spoofing, CAPTCHA solving, or rate-limit evasion.
- No automatic link replacement.

## Tests

```bash
python3 -m unittest discover -s tests -v
```
