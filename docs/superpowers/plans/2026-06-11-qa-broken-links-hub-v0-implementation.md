# QA Broken Links Hub V0 Implementation Plan

Date: 2026-06-11
Status: implementation-ready plan, not started

## Goal

Ship the first free KikuAI hub MVP for QA Broken Links as a browser-local file analyzer.

The user drops or pastes CSV, HTML, or Markdown. The tool parses locally, extracts monetized/recommendation links, runs deterministic rules, and exports a conservative report. It must not live-check third-party destinations in the browser path.

## Target Repository Surface

Observed KikuAI hub structure:

- Nuxt app under `kikuai-site-nuxt/`.
- Existing browser-local tools use:
  - `components/<ToolName>.vue`
  - `lib/<tool-name>.js`
  - `pages/tools/<tool-route>.vue`
  - `pages/tools/index.vue`
  - `test/<tool-name>.test.mjs`
- Test runner pattern: `node --test test/<tool>.test.mjs`.
- Tool index cards already include a private "Broken-link QA" placeholder.

Current execution caution:

- The inspected KikuAI hub worktree already has unrelated dirty changes for another tool.
- Implement QA Broken Links in a clean branch/worktree or after those changes are handled.
- Do not mix QA Broken Links edits with the current Merchant Feed work.

## Non-Goals

- No live HTTP checks.
- No redirect-chain verification.
- No product availability checks.
- No AI verdicts.
- No backend upload or storage.
- No payment, paywall, checkout, or paid-report request flow.
- No public Telegram scraping.
- No outreach, lead discovery, or monitoring.

## Proposed Route And Files

Route:

- `/tools/affiliate-link-health-checker/`

Suggested files:

- `kikuai-site-nuxt/components/AffiliateLinkHealthChecker.vue`
- `kikuai-site-nuxt/lib/affiliate-link-health-checker.js`
- `kikuai-site-nuxt/pages/tools/affiliate-link-health-checker.vue`
- `kikuai-site-nuxt/test/affiliateLinkHealthChecker.test.mjs`
- update `kikuai-site-nuxt/pages/tools/index.vue`
- update `kikuai-site-nuxt/package.json` with `check:affiliate-link-health`
- update `kikuai-site-nuxt/test/siteIntegrity.test.mjs` only if route inventories are asserted there
- update `kikuai-site-nuxt/public/llms.txt`, `llms-full.txt`, and `sitemap.xml` only if the existing build process does not regenerate them

## Core Data Model

Input row:

- `rowNumber`
- `sourceType`: `csv`, `html`, or `markdown`
- `sourceReference`
- `sourceContext`
- `anchorText`
- `originalUrl`

Normalized link:

- `normalizedUrl`
- `scheme`
- `hostname`
- `path`
- `queryKeys`
- `registrableDomain` if implemented locally without a heavy dependency
- `dedupeKey`

Finding:

- `id`
- `severity`: `info`, `warning`, or `needs_verification`
- `category`: `invalid`, `inventory_only`, `needs_verification`, or `quality_warning`
- `ruleId`
- `title`
- `explanation`
- `originalUrl`
- `sourceReference`
- `sourceContext`
- `anchorText`
- `recommendedAction`
- `confidence`

## Parser Scope

CSV:

- Accept `url`, `link`, `href`, `target_url`, `original_url`, `destination`.
- Preserve `source_url`, `page_url`, `source`, `source_reference`.
- Preserve `anchor_text`, `anchor`, `text`.
- Preserve `context`, `source_context`, `description`.
- If only `url` exists, still produce a report with source/context warnings.

HTML:

- Parse uploaded or pasted markup with browser DOM APIs.
- Extract `a[href]`.
- Use anchor text and nearby text as context.
- Ignore `mailto`, `tel`, `javascript`, `data`, and fragment-only links for the commercial-link queue.
- Do not fetch linked pages.

Markdown:

- Extract `[anchor](url)` links.
- Extract bare HTTP(S) URLs.
- Preserve surrounding line as context where feasible.
- Do not fetch linked pages.

## Initial Rule Set

Deterministic rules only:

1. `invalid_url`: URL cannot be parsed as HTTP(S).
2. `unsupported_scheme`: non-HTTP(S) destination.
3. `duplicate_exact_url`: same original URL appears more than once.
4. `duplicate_normalized_destination`: normalized destination duplicates another row.
5. `missing_context`: row has no source URL, anchor, or surrounding context.
6. `affiliate_tracking_detected`: query keys such as `tag`, `ref`, `aff`, `affiliate`, `partner`, `subid`, `clickid`, `irclickid`, `sid`.
7. `campaign_tracking_detected`: `utm_*`, `gclid`, `fbclid`, `msclkid`, `mc_cid`, `mc_eid`.
8. `marketplace_or_shortener`: Amazon, AliExpress, eBay, app stores, common shorteners, and redirector-style hosts.
9. `redirector_pattern`: path/query contains `go`, `out`, `redirect`, `url=`, `target=`, or `u=`.
10. `commercial_context_detected`: nearby text suggests product, review, best, deal, buy, coupon, alternative, recommended, or tool.

Important boundary:

- `affiliate_tracking_detected`, `campaign_tracking_detected`, and `marketplace_or_shortener` are inventory or verification-queue signals, not broken-link findings.
- The free MVP must not produce a `broken` label for remote destinations.

## Report Output

On-screen:

- total links parsed;
- commercial/recommendation-looking links;
- affiliate/tracking inventory count;
- duplicate count;
- invalid/unsupported count;
- `needs_verification` count;
- source/context warning count;
- table with filters for category and severity.

Downloads:

- CSV report;
- JSON report;
- Markdown summary;
- HTML summary.

Required copy:

- "This tool does not live-check remote destinations."
- "Files stay in your browser."
- "Marketplace, shortener, and affiliate-network links need verification before owner-facing claims."

## UI Notes

Use the existing KikuAI tool style:

- header back to KikuAI/tools;
- large drop zone;
- `Try sample` button;
- primary `Run analysis` button;
- result metrics panel;
- issue table;
- export buttons;
- no nested cards inside cards where avoidable.

Use icons from `lucide-vue-next`, likely:

- `Link2Off`
- `Upload`
- `FileSearch`
- `Download`
- `ShieldCheck`
- `AlertTriangle`
- `RotateCcw`

## Test Plan

Unit tests for `lib/affiliate-link-health-checker.js`:

- parses CSV with only `url`;
- maps recommended CSV columns;
- extracts HTML `a[href]` without network fetch;
- extracts Markdown links and bare URLs;
- flags malformed URLs;
- ignores unsupported schemes in the commercial queue while reporting them;
- preserves affiliate/tracking query parameters;
- detects exact and normalized duplicates;
- classifies marketplace/shortener/redirector patterns as `needs_verification`;
- exports CSV/JSON/Markdown/HTML reports;
- sample analysis returns stable counts.

Page/integration tests:

- page route includes privacy/no-live-check copy;
- tools index links to the new route;
- no backend API endpoint is required by the component.

Manual QA:

- run the tool on a small synthetic CSV;
- run the tool on pasted HTML;
- run the tool on pasted Markdown;
- verify exports download and contain no invented live status;
- verify responsive layout at mobile and desktop widths.

Suggested commands after implementation:

```bash
cd kikuai-site-nuxt
pnpm check:affiliate-link-health
pnpm check:site
pnpm generate
```

## Acceptance Criteria

V0 passes when:

- CSV, HTML, and Markdown inputs all produce a report.
- The tool runs with no backend and no third-party URL fetch.
- Reports preserve original URLs and affiliate/tracking parameters.
- Findings are deterministic and traceable to local input.
- Remote link status is never presented as verified.
- Exports work for CSV, JSON, Markdown, and HTML.
- The tools index links to the new page.
- Tests pass.
- Browser QA shows no blank page, overlapping text, or broken responsive layout.

## Implementation Order

1. Create `lib/affiliate-link-health-checker.js` with parser, normalizer, rules, and report exporters.
2. Add unit tests and fixtures until the library contract is stable.
3. Build `AffiliateLinkHealthChecker.vue` around the library.
4. Add the `/tools/affiliate-link-health-checker/` page.
5. Replace the tools index placeholder with a link to the page.
6. Add package script and route integrity tests.
7. Run automated tests.
8. Start dev server and verify with browser screenshots on desktop and mobile.

## Parking Gate

Do not continue toward paid exports, verified reports, or monitoring from this implementation alone.

The paid path remains gated on:

- repeated user uploads or strong usage signal from the free tool;
- a second stronger proof batch reaching at least `5` manually confirmed meaningful issues per `100` links;
- low false positives and manageable QA time.
