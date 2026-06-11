# First Web-Affiliate Proof Batch Runbook

Date: 2026-06-11
Status: executed
Related PRD: `docs/affiliate-revenue-link-health-mvp-prd.md`
Result memo: `docs/research-sprint/first-web-affiliate-proof-batch-results.md`

## Purpose

Run measured proof batches around the free hub drop-in analyzer.

This runbook is for the current hub-first path: `100` rights-clean public affiliate/recommendation links, not the older `100 + 100` Telegram-vs-web lane comparison.

Execution note: Nick approved operator-selected public sources for the first run, so the first batch ran as an operator proof before the public hub MVP shipped. It checked `100` links, manually confirmed `3` meaningful issues, and did not pass the `>=5` confirmed issues per `100` links gate. See the result memo for details.

## What This Batch Should Prove

- A rights-clean public or owner-provided source set can produce `100` usable monetized/recommendation links.
- Local analyzer findings are useful enough to justify manual verification.
- `needs_verification` does not become a noisy generic broken-link queue.
- Manual QA can find at least `5` meaningful confirmed issues per `100` links.
- False positives and blocked/ambiguous cases stay within gates.

## Source Rules

Allowed:

- public affiliate/recommendation pages;
- owner-provided CSV/HTML/Markdown exports;
- public resource pages with clear commercial recommendations;
- public SaaS/tools directories with visible outbound recommendations.

Disallowed:

- public Telegram scraping;
- private or authenticated pages;
- paywalled pages;
- pages that disallow access through robots.txt when collection is used;
- medical, legal, financial advice, government, education, or public-institution pages;
- giant-company or major-media outreach targets;
- pages where an issue cannot be described without scare claims.

## Sample Selection

Target source mix:

- `40` links from affiliate roundup/review pages.
- `30` links from Amazon/marketplace-style recommendation pages.
- `20` links from SaaS/tools directories.
- `10` links from creator/resource pages.

If one category cannot be collected cleanly, replace it with another public recommendation-page source and record the reason.

## Input Template

Use CSV with this minimum shape:

```csv
url,source_url,anchor_text,context,notes
https://merchant.example/product,https://publisher.example/best-tools,Recommended tool,"Best tools list row",public_page
```

For the current Python operator CLI, normalize to:

```csv
sample_id,lane,consent_basis,source_reference,source_context,original_url
web-001,web_affiliate,public_page,https://publisher.example/best-tools,"Recommended tool - Best tools list row",https://merchant.example/product
```

## Measurement Fields

Track:

- `checked_links`
- `candidate_findings`
- `needs_verification_count`
- `invalid_count`
- `inventory_only_count`
- `manually_confirmed_issues`
- `false_positives`
- `blocked_or_ambiguous`
- `qa_minutes`
- `direct_cost_usd`
- `value_clarity_score`
- `notes`

## Manual QA Gate

No issue can be used as evidence until a human verifies:

- source page context;
- target URL;
- visible anchor/context;
- evidence category;
- screenshot or compact evidence note;
- issue type;
- confidence;
- recommended action;
- why the result is not merely blocked, geo-dependent, login-gated, or ambiguous.

## Pass Gates

Pass only if:

- `100` links are checked;
- at least `5` meaningful issues are manually confirmed;
- false positives are `<=20%`;
- blocked/ambiguous cases are `<=20%`;
- QA time is `<60` minutes per `100` links;
- direct infrastructure/API cost is `<$5`;
- no spam, outreach, scraping, proxy, CAPTCHA, or rate-limit evasion is required.

## Stop Conditions

Stop or reshape if:

- source collection takes too long;
- links are mostly generic non-commercial links;
- `needs_verification` is too noisy;
- most candidates require live checking to explain value;
- the batch cannot produce buyer-visible examples without overclaiming;
- any example would require scare copy or unsupported revenue-loss claims.

## Output

Produce:

- normalized input CSV;
- analyzer report;
- manual QA decisions;
- proof-batch metrics summary;
- short decision memo: `continue_verified_report_test`, `reshape_rules`, `reshape_icp`, or `park`.

## Current Status

The first `100`-link source set was collected from operator-selected public pages after Nick approved self-selection.

The next blocker is not source approval. It is whether a second, stronger source hypothesis can produce `>=5` manually confirmed meaningful issues per `100` links without increasing ambiguity, manual QA time, or rights risk.
