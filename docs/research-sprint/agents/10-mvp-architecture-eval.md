# MVP Architecture And Eval Research
This is repo-real, not generic advice: the codebase is a Python `3.11+` stdlib-only package (`revenue-link-health`) with a `linkhealth` CLI, deterministic checker, CSV/JSONL evidence pipeline, and lane-level report logic. The recommendation below is anchored to that actual implementation, not a memory-based broken-link template.

## Executive Verdict
V1 should stay **browser-local and deterministic**. Add richer import/schema support, stronger local normalization and reporting, and a frozen eval harness. Do **not** move live verification, AI verdicting, or outreach into the browser-local path.

The repo already has a separate operator CLI for live checks and a benchmark/report loop, but the product direction in the design spec is clear: the public MVP is a local file analyzer that produces conservative risk reports, not live broken-link claims ([design spec](../../docs/superpowers/specs/2026-06-11-qa-broken-links-hub-drop-in-v0-design.md#L12), [README](../../README.md#L3)).

## V1 architecture recommendation
1. Keep the browser-local core deterministic:
   - CSV remains the primary contract.
   - Add permissive alias mapping for common exports.
   - Support HTML and Markdown as best-effort secondary parsers.
   - Preserve a strict “what was verified vs what was inferred” split.

2. Expand the local rule engine, not the verdict engine:
   - URL validity checks.
   - Duplicate and normalized-destination dedupe.
   - Affiliate/tracking pattern detection.
   - Missing context / weak-evidence warnings.
   - High-risk link family classification.
   - Conservative report generation with explicit “not verified” sections.

3. Keep live verification out of the browser path:
   - The current design spec explicitly forbids live broken-link claims in the browser-only MVP.
   - If live verification is retained at all, keep it as an explicit operator-run CLI or paid fulfillment step, not an automatic product behavior ([spec](../../docs/superpowers/specs/2026-06-11-qa-broken-links-hub-drop-in-v0-design.md#L16), [CLI](../../linkhealth/cli.py#L37)).

4. Keep AI advisory only:
   - AI can help summarize, cluster, and explain.
   - AI must not decide final broken/unavailable status.
   - AI must not replace deterministic rules or human QA.

5. Add export and review surfaces before dashboards:
   - Local HTML/CSV/Markdown report.
   - QA decision file.
   - Optional PDF-ready export later, but not a full dashboard yet.

## Eval dataset design
Build a **versioned frozen corpus**, not just a demo folder.

1. Core corpus slices:
   - Parser golden set: CSV, HTML, and Markdown inputs with aliases, malformed rows, missing fields, and context variations.
   - URL normalization set: duplicates, redirects, fragments, tracking parameters, default ports, mixed case, and punycode edge cases.
   - Risk-pattern set: affiliate, marketplace, shortener, redirector, and tracking-link examples.
   - Live-verification set: known 200/404/410/302/loop/5xx/403/429/login/CAPTCHA cases, if you keep the CLI checker.
   - Human QA set: candidate issues with explicit confirm/reject labels.
   - Adversarial set: cases designed to trigger false positives.

2. Label schema:
   - `url_ok`
   - `normalized_key`
   - `duplicate_group`
   - `commercial_intent`
   - `affiliate_or_tracking_signal`
   - `live_status_class`
   - `blocked_or_ambiguous_class`
   - `human_verdict`
   - `evidence_required`
   - `notes_on_why_not_auto`

3. Corpus governance:
   - Freeze the corpus.
   - Version it.
   - Separate dev vs eval splits.
   - Require every label to be traceable to local evidence or operator note.
   - Keep rights-clean inputs only, matching the PRD’s no-scrape/no-evasion boundary ([PRD](../../docs/affiliate-revenue-link-health-mvp-prd.md#L145)).

4. Minimum useful size:
   - For V1 parser/rule eval: a few hundred rows is enough if it is diverse.
   - For the dual-lane product question in the PRD: keep the `100 + 100` lane benchmark as the headline eval ([README](../../README.md#L121), [PRD](../../docs/affiliate-revenue-link-health-mvp-prd.md#L43)).

## Metrics and thresholds
Use two metric groups: **trust metrics** and **value metrics**.

1. Trust metrics:
   - Parser exact-match accuracy on the frozen corpus.
   - URL normalization and dedupe precision.
   - False “broken” rate from the browser-local path: target zero, because that path must not claim live brokenness.
   - Manual overturn rate of automated candidate issues.
   - Share of findings with deterministic evidence attached.

2. Value metrics:
   - Confirmed issues per 100 links.
   - Candidate false-positive rate.
   - Blocked/ambiguous rate.
   - Manual QA minutes per 100 links.
   - Direct cost per 100 links.
   - Value clarity score.

3. Thresholds already encoded in the repo and PRD:
   - `>= 100` checked links per lane.
   - `>= 5` confirmed issues in a selected lane.
   - false-positive rate `<= 20%`.
   - blocked/ambiguous rate `<= 20%`.
   - direct cost `< $5 / 100 links`.
   - QA time `< 60 min / 100 links`.
   - value clarity `>= 4/5` ([README](../../README.md#L121), [report gates](../../linkhealth/report.py#L18)).

4. Additional V1 thresholds I would add:
   - Zero AI-driven final verdicts.
   - Zero “broken” claims without deterministic evidence.
   - 100% traceability from finding to rule ID and source row.
   - Parser failure rate below 1% on accepted input types.

## AI/non-AI boundary
AI can help here, but only in advisory roles.

1. Safe AI uses:
   - Drafting plain-language report summaries.
   - Grouping similar links by product/category.
   - Suggesting likely commercial context labels.
   - Drafting conservative reviewer prompts.

2. AI must not decide:
   - Final broken/unavailable status.
   - Whether an inaccessible page is actually broken.
   - Whether a link is commercial enough to count as evidence.
   - Lane selection.
   - Pricing or outreach decisions.
   - QA verdicts.

3. Non-AI must own:
   - URL parsing and normalization.
   - Duplicate detection.
   - Rule evaluation.
   - Report metrics.
   - Gate decisions.
   - Any claim that would matter externally.

That boundary matches the V0 design spec, which explicitly allows only advisory AI and forbids AI final verdicts ([spec](../../docs/superpowers/specs/2026-06-11-qa-broken-links-hub-drop-in-v0-design.md#L153)).

## Implementation risk list
1. Current normalization is too light for trust-sensitive dedupe.
   - It lowercases scheme/host and strips fragments, but does not canonicalize default ports, IDNA/punycode, or deeper path equivalence ([checker](../../linkhealth/checker.py#L67)).

2. Current live-check CLI is outside the browser-local MVP boundary.
   - `check` and `collect-web` still do live fetching.
   - That is fine as an operator tool, but it should not leak into the browser-local product promise ([CLI](../../linkhealth/cli.py#L37), [web](../../linkhealth/web.py#L123)).

3. The benchmark/report gates are threshold-driven and small-sample sensitive.
   - A lane can look “best” before the evidence base is large enough.
   - Keep the 100-link-per-lane rule hard.

4. The evidence schema is permissive.
   - Stronger validation and schema versioning will be needed as soon as you support more import shapes ([workflow](../../linkhealth/workflow.py#L14)).

5. The test harness currently depends on temp dirs and loopback HTTP servers.
   - In this sandbox, the suite failed because there was no usable temp directory and loopback binds were denied.
   - That is environment-specific, but it means the harness should lean harder on pure in-memory fixtures for eval portability.

6. The browser-local spec and the current CLI are intentionally different products.
   - Keep that separation crisp so the public MVP does not inherit live-fetch trust debt from the operator workflow.

## 2-week technical plan
1. Week 1: freeze the eval contract.
   - Define corpus schema.
   - Add frozen parser/rule fixtures.
   - Add normalization golden tests.
   - Add conservative report snapshots.
   - Separate “local analyzer” claims from “live checker” claims.

2. Week 1: harden the local analyzer.
   - Add CSV alias support.
   - Add HTML and Markdown import fixtures.
   - Add deterministic rule IDs and evidence text.
   - Add explicit “what this did not verify” report sections.

3. Week 2: build the evaluation harness.
   - Create the frozen benchmark corpus.
   - Add automated scoring for parser precision, dedupe accuracy, and report completeness.
   - Add human QA decision ingestion.
   - Compute value metrics and trust metrics per run.

4. Week 2: add the product decision gates.
   - Require 100 links per lane.
   - Report false-positive, ambiguous, cost, and QA-time thresholds.
   - Preserve manual signoff for any claim that would be externally visible.
   - Keep live verification as a separate explicit operator path if you retain it.

## Sources and assumptions
Sources used from the repo:
- [README.md](../../README.md#L3)
- [affiliate-revenue-link-health-mvp-prd.md](../../docs/affiliate-revenue-link-health-mvp-prd.md#L13)
- [qa-broken-links-hub-drop-in-v0-design.md](../../docs/superpowers/specs/2026-06-11-qa-broken-links-hub-drop-in-v0-design.md#L12)
- [pyproject.toml](../../pyproject.toml#L5)
- [linkhealth/cli.py](../../linkhealth/cli.py#L33)
- [linkhealth/checker.py](../../linkhealth/checker.py#L67)
- [linkhealth/report.py](../../linkhealth/report.py#L57)
- [linkhealth/workflow.py](../../linkhealth/workflow.py#L14)
- [linkhealth/benchmark.py](../../linkhealth/benchmark.py#L64)
- [linkhealth/web.py](../../linkhealth/web.py#L123)
- [linkhealth/models.py](../../linkhealth/models.py#L8)

Assumptions:
- I did not use web search because the question is primarily about repo-local architecture, not a current external technical claim.
- The repo is Python `3.11+`, stdlib-only, and has no framework-specific dependency to optimize around.
- I attempted the test suite, but this environment blocked temp-dir creation and loopback server binds, so I could not fully validate runtime behavior here.

If you want, I can turn this into a concrete V1 scope checklist and a frozen eval-corpus schema next.