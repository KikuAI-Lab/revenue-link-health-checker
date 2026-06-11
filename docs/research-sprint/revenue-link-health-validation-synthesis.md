# Revenue Link Health Checker - Multi-Agent Validation Synthesis

Date: 2026-06-11
Status: validation synthesis, not a SaaS build approval
Inputs: 10 focused subagent reports under `docs/research-sprint/agents/`

## Executive Verdict

Continue, but keep the project deliberately small.

The strongest surviving wedge is a free, local-first file analyzer for monetized/recommendation links, followed by a manually verified paid report only if the free checker reveals buyer-visible value. Do not lead with a SaaS dashboard, Telegram bot, Chrome extension, WordPress plugin, crawler fleet, bulk outreach system, or autonomous monitoring product.

The current best first ICP is not AliExpress/Telegram. It is niche affiliate review sites, Amazon/marketplace roundup publishers, and small content operators with evergreen commercial recommendation pages. AliExpress/Telegram can remain a comparison lane only through explicit admin opt-in or supplied exports.

## Where We Are Now

This project is still in validation, but it is past pure desk research.

The active shape should be:

- Free MVP: local-first drop-in file analyzer in the KikuAI tools hub.
- User input: CSV, JSONL/NDJSON, pasted HTML, pasted Markdown, and later selected export formats.
- Output: conservative risk report with explicit evidence and "not verified" boundaries.
- Paid path: manual verified money-page report, not subscription monitoring.
- Technical posture: deterministic rules first; AI advisory only; no AI final verdicts.

Important wording: say `local-first` unless the actual shipped UI runs fully in the browser. Say `browser-local` only for the KikuAI hub implementation once file parsing and report generation really happen client-side.

## Consensus Across Agents

The agents strongly agreed on six points:

1. Generic broken-link checking is commoditized by free tools, SEO suites, browser extensions, and OSS.
2. Affiliate/revenue-link context is real, but trust dies quickly if the checker overclaims.
3. The MVP should report risk signals and candidate issues, not definitive live availability unless there is deterministic or human-reviewed evidence.
4. Telegram/AliExpress is not a clean first wedge unless every source is opt-in and admin-provided.
5. Distribution should start with exact-intent search, GitHub/open-source credibility, helpful community posts, and short demos.
6. The first paid signal should be a fixed-scope report, not monitoring.

## Recommended Product Shape

### Free MVP

Build and ship a free local-first analyzer:

- accepts a user-provided file or pasted content
- runs on the user's machine
- extracts and normalizes links
- classifies links into `invalid`, `inventory_only`, and `needs_verification`
- preserves source row, source context, original URL, normalized key, rule ID, and evidence
- exports Markdown, HTML, CSV, and JSON/JSONL
- clearly says what was not verified

The free MVP should be useful without payment. Its job is to prove that users bring real files and that the report produces credible "I should check this" moments.

### Paid Offer After Signal

Do not charge for the first free checker. If users ask for help or report quality is strong, test:

- `$19-$29` polished export/report pack
- `$49` one verified money-page report
- `$99` small verified batch report

The stronger agent recommendation is that `$9-$19` is too low for human verification. It can work for a purely automated export, but it makes a manually verified report look cheap and less credible.

Monthly monitoring should wait until paid reports prove repeatability.

## ICP Priority

Ranked first targets:

1. Niche affiliate review site owners and Amazon/marketplace roundup publishers.
2. SaaS/tool directories and resource-page owners with visible commercial recommendations.
3. Opt-in Telegram/AliExpress admins, only as a later comparison lane with explicit consent.

Reasoning:

- Web affiliate pages have clearer commercial context and higher likely willingness to pay.
- Telegram/AliExpress has faster link churn but lower ARPU, more ambiguity, and stricter source-rights constraints.
- A public Telegram scraping path should remain a hard non-goal.

## Input And Schema Recommendation

Keep the canonical row model small:

- `sample_id`
- `lane`
- `original_url`
- `source_reference`
- `source_context`
- `consent_basis`

Add optional metadata, not required complexity:

- `source_format`
- `source_type`
- `page_title`
- `anchor_text`
- `network`
- `status_code`
- `final_url`
- `redirect_hops`
- `canonical_url`
- `nofollow`
- `published_at`
- `lastmod`
- `notes`
- `extras_json`

Prioritized input surfaces:

1. CSV and JSONL/NDJSON manifests.
2. Pasted HTML and Markdown.
3. WordPress XML/WXR exports.
4. Screaming Frog CSV/XLS/XLSX/Google Sheets exports.
5. BetterLinks CSV exports.
6. Ahrefs CSV reports.
7. Sitemaps and URL lists.
8. Google Search Console pages as discovery input, not as the core link schema.
9. Telegram/AliExpress admin exports only when opt-in.

## Reliable Rulebook

Auto-resolve only deterministic local findings:

- malformed URL
- unsupported non-HTTP scheme
- exact normalized duplicate
- missing source context
- affiliate/tracking parameter inventory
- marketplace, shortener, redirector, and app-store family classification

Never auto-claim these as broken:

- `403`
- `429`
- CAPTCHA
- login wall
- geo block
- marketplace availability
- shortener final state
- wrong-region store result
- out-of-stock product state

Those belong in `needs_verification`, not `broken`.

Canonicalization should preserve affiliate and tracking query parameters by default. Never strip `tag`, `ref`, `aff`, `subid`, `utm_*`, `gclid`, `fbclid`, or similar parameters when evidence traceability matters.

## Technical Implementation Direction

For the KikuAI hub MVP:

1. Use a static browser page with a file drop zone and paste box.
2. Parse files locally with a Web Worker so large files do not freeze the UI.
3. Keep the rule engine deterministic and test-backed.
4. Build a frozen eval corpus before adding more rules.
5. Generate reports locally.
6. Avoid backend storage, user accounts, and live checking in the free path.

OSS can help with the substrate:

- Markdown parsing: `micromark`
- HTML parsing: `parse5` or a lightweight DOM parser
- URL parsing and normalization: WHATWG URL behavior plus a careful normalizer
- domain grouping: `tldts` or `psl`
- regression tests: WHATWG/WPT URL fixtures

Avoid making GPL tools a core dependency unless the licensing choice is intentional. Use generic link checkers such as `lychee` as references or external validation, not as the product.

## AI Boundary

Do not use AI in the hot path for V1 verdicts.

Safe AI uses later:

- summarize a report
- group similar rows
- draft conservative reviewer notes
- explain rule categories

Unsafe AI uses:

- final broken/unavailable verdict
- legal/compliance conclusions
- revenue-loss estimates
- outreach personalization from raw link data
- selecting which lane wins

For now, no model is required. If an optional AI summary is added later, it should be opt-in and should not receive raw customer files unless the privacy policy and UI clearly say so.

## Cost And Infrastructure

The free MVP should be almost free to operate:

- static hosting only
- no backend compute for analysis
- no LLM spend in the default flow
- no database requirement
- user machine does parsing and report generation

Costs begin when you add:

- hosted uploads
- live checks
- screenshots
- geolocation checks
- AI summaries over raw links
- manual verified paid reports

The most expensive hidden cost is manual QA time, not compute. Keep the hard gate: less than `60` QA minutes per `100` checked links.

## Distribution Direction

Best current path:

1. Exact-intent SEO pages around `affiliate link checker`, `broken affiliate links`, `broken Amazon links`, `recommendation page link checker`, and `check links in HTML CSV Markdown`.
2. GitHub/open-source repo with sample files, transparent rules, and issue templates for edge cases.
3. Help-first posts in WordPress/SEO communities only where rules allow.
4. Short YouTube demos showing a real local scan and report.
5. No broad cold outreach; no scraping-based lead lists.

The AI-search implication from the Ahrefs-style research Nick shared is consistent with this: create useful, citable, comparison-friendly assets and demos. Do not buy "AI SEO" tricks. A page that explains the tool, its limits, alternatives, and specific workflows is more likely to be useful than a generic landing page.

## Trust, Privacy, And Legal Boundaries

Safe claims:

- local-first
- no account for the free workflow
- no file upload for the free workflow
- no backend analysis for the free workflow
- public pages only if collection is used
- robots.txt respected for public-page collection
- no public Telegram scraping
- no proxy rotation, CAPTCHA solving, identity spoofing, or rate-limit evasion
- ambiguous results stay ambiguous
- human QA required before confirmed paid-report claims

Dangerous claims:

- SOC2 compliant
- GDPR compliant
- enterprise-grade security
- legal compliance guaranteed
- 100% accurate
- zero false positives
- exact lost revenue
- nothing ever leaves your device if analytics, payments, email, or hosted reports are present

Before paid reports, add:

- privacy policy
- terms/scope page
- refund/rework policy
- data retention and deletion wording
- clear statement when data leaves the user's machine
- payment processor boundary

This is operational risk guidance, not legal advice.

## Evidence Used

Local artifacts:

- `README.md`
- `docs/affiliate-revenue-link-health-mvp-prd.md`
- `docs/superpowers/specs/2026-06-11-qa-broken-links-hub-drop-in-v0-design.md`
- `linkhealth/`
- `tests/`
- 10 subagent reports in `docs/research-sprint/agents/`

External evidence categories from agent reports:

- competitor pricing and positioning: AffilGuard, PageRadar, AMZ Watcher, Lasso, BetterLinks, ThirstyAffiliates, Ahrefs, Check My Links, Semrush, Brokenly
- export/schema sources: WordPress, Screaming Frog, BetterLinks, Google Search Console, Ahrefs
- OSS references: lychee, linkchecker, markdown-link-check, html-proofer, micromark, parse5, cheerio, linkedom, jsdom, normalize-url, whatwg-url, tldts, psl, WPT URL tests
- trust/privacy/legal sources: FTC disclosure guidance, California DOJ privacy-policy guidance, Telegram Bot API constraints

## Assumptions And Uncertainties

Still unproven:

- whether real users will upload/drop files into the free tool
- whether reports produce enough "this saved me money" moments
- whether `5+` confirmed meaningful issues per `100` links is realistic in the chosen lane
- whether false positives can stay below `20%`
- whether manual QA can stay below `60` minutes per `100` links
- whether users will pay `$49-$99` for a verified report
- whether exact-intent SEO pages can rank or be cited quickly enough to matter
- whether browser-local implementation quality can match the local Python proof workflow

Claims to verify before public copy:

- current competitor prices
- current extension user counts
- current OSS star/release counts
- any compliance or privacy statement beyond local-first mechanics

## Kill Criteria

Park or reshape the project if any of these happen:

- no rights-clean sample source can produce `100` usable links
- selected lane produces fewer than `5` confirmed meaningful issues per `100` links
- false positives exceed `20%`
- blocked/ambiguous cases exceed `20%`
- manual QA exceeds `60` minutes per `100` links
- prospects say this is only a generic broken-link checker
- users primarily ask for dashboard/monitoring before they value the report
- distribution requires spam, scraping, or broad cold outreach
- the free tool cannot explain uncertainty clearly enough for users to trust it

## Recommended Next Action

Rewrite the PRD around a free KikuAI hub drop-in file analyzer as P0, then run one measured proof batch:

1. Build or finalize the browser-local MVP with CSV/HTML/Markdown ingest.
2. Create a frozen eval corpus with synthetic and rights-clean examples.
3. Test `100` public affiliate/recommendation links from rights-clean sources.
4. Manually verify every candidate issue.
5. Decide whether the next step is a `$49` verified report test or a pivot.

Do not start autonomous monitoring or Telegram productization before this proof batch passes.
