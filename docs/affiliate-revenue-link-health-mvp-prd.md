# Revenue Link Health Checker - Free Hub Drop-In MVP PRD

Date: 2026-06-11
Status: P0 free local-first hub drop-in PRD, not a SaaS approval
Audience: coding agent, product strategist, solo operator
Evidence base: `docs/research-sprint/revenue-link-health-validation-synthesis.md`, `docs/research-sprint/first-web-affiliate-proof-batch-results.md`, and `docs/research-sprint/agents/`

## 1. Russian Executive Summary

Первый MVP должен быть бесплатным инструментом в KikuAI hub: пользователь кидает CSV/HTML/Markdown файл, анализ выполняется локально на его устройстве, а результатом становится аккуратный risk report по monetized/recommendation links.

Это не SaaS, не Telegram-бот, не Chrome extension, не WordPress plugin, не мониторинг, не crawler fleet и не outreach-система. P0 не должен обещать live broken-link verification, потому что браузерный sandbox, CORS, marketplace-блокировки и редиректы делают такие обещания ненадежными.

Лучший первый buyer/ICP: niche affiliate review sites, Amazon/marketplace roundup publishers, SaaS/tools directories и resource-page owners с явными коммерческими рекомендациями. AliExpress/Telegram остается later comparison lane только через explicit admin opt-in или admin-provided exports.

Цель P0: доказать, что free local-first analyzer дает понятный value без backend cost, AI cost и sales calls. Платная логика появляется только после сигнала: сначала `$49-$99` manually verified report, не subscription monitoring.

Первый self-selected public-page proof batch проверил `100` web-affiliate links и вручную подтвердил `3` meaningful issues. Это доказывает, что проблема реальна, но пока не доказывает достаточную плотность для платного verified report без более сильной source-selection гипотезы.

## 2. Product Decision

Build a free local-first file analyzer first.

Decision:

- Build P0 as a KikuAI hub drop-in file tool.
- Keep the first public MVP free.
- Analyze user-supplied files locally.
- Generate conservative local reports.
- Treat findings as risk signals and verification queues, not definitive live broken-link claims.
- Use deterministic rules as the source of truth.
- Keep AI optional and advisory only.
- Delay paid reports, monitoring, outreach, Telegram, browser extensions, WordPress, and SaaS dashboards until the free analyzer shows real pull.

This replaces the older dual-lane P0 as the active first MVP. The dual-lane `100 + 100` benchmark remains useful as a research method, but it is no longer the public product shape.

## 3. Problem Statement

Small publishers, affiliate site owners, roundup editors, and resource-page owners often maintain monetized recommendation links in spreadsheets, CMS exports, HTML snippets, Markdown drafts, or crawler exports. Existing tools can check generic broken links, but they are often:

- too broad for a quick monetized-link preflight;
- too tied to WordPress, SEO suites, dashboards, or monitoring subscriptions;
- too eager to label blocked or ambiguous destinations as broken;
- too invasive for users who do not want to upload link inventories to a third-party service;
- too weak at explaining what was verified versus inferred.

The P0 problem is not "check every link on the internet." It is: help a user inspect their own monetized/recommendation-link file locally and decide which links need manual or paid verification.

## 4. P0 Goal

Within P0, ship a free local-first analyzer that can:

- accept a dropped or pasted user file;
- extract URL rows and visible context;
- classify local risk signals;
- produce a downloadable report;
- explain uncertainty clearly;
- run without accounts, backend analysis, API keys, live URL fetching, or LLM usage.

P0 must prove:

- users can bring suitable files without handholding;
- local rules can surface credible monetized-link review candidates;
- reports are useful even when they do not perform live verification;
- the product can run with near-zero infrastructure and AI cost;
- the next paid step, if any, should be a verified report rather than a dashboard.

P0 must not prove:

- paid conversion;
- SEO scale;
- ongoing monitoring retention;
- live third-party link verification;
- support for every affiliate network;
- Telegram bot demand;
- WordPress plugin demand;
- exact lost revenue calculations.

## 5. Primary ICP

Primary ICP:

- niche affiliate review site owners;
- Amazon/marketplace roundup publishers;
- small content operators with evergreen money pages;
- SaaS/tools directories;
- creator/resource-page owners with visible commercial recommendations.

Secondary/later ICP:

- opt-in Telegram/AliExpress channel admins who explicitly provide exports or invite a bot for a bounded test.

Why the primary ICP wins first:

- the page context is easier to understand;
- commercial intent is visible;
- willingness to pay is more plausible than low-ARPU Telegram deal channels;
- the workflow maps naturally to file upload/export/report;
- the product can stay no-call and privacy-light.

## 6. Positioning

P0 positioning:

> A free local-first checker that turns your affiliate, roundup, or recommendation-link file into a conservative risk report.

Supporting copy:

- Files stay local in the free workflow.
- No account.
- No upload.
- No live fetch.
- No AI required.
- Clear separation between `invalid`, `inventory_only`, and `needs_verification`.

Not positioning:

- broken-link checker for every website;
- SEO audit;
- affiliate analytics platform;
- WordPress link manager;
- Telegram scraping bot;
- revenue-loss calculator;
- compliance certification.

## 7. P0 / P1 / P2 / P3 Scope

### P0: Free Hub Drop-In Analyzer

In scope:

- CSV input with flexible URL column aliases.
- Pasted or uploaded HTML.
- Pasted or uploaded Markdown.
- Local parsing and analysis.
- Deterministic URL normalization.
- Deterministic risk rules.
- Local report preview.
- Downloadable Markdown/HTML/CSV/JSON report.
- Synthetic and rights-clean fixture corpus.
- Clear "what this did not verify" section.

Out of scope:

- live HTTP status checks in the browser path;
- redirect-chain verification;
- product availability checks;
- marketplace geo checks;
- payment;
- user accounts;
- hosted uploads;
- database;
- email capture as a required step;
- outreach automation.

### P1: Verified Report Test

Only after P0 usage signal:

- `$19-$29` polished export/report pack if users want better output but no human verification;
- `$49` one verified money-page report;
- `$99` small verified batch report;
- manual verification with screenshots/evidence;
- explicit privacy, retention, refund, and scope terms.

### P2: Live Verification Or Monitoring Beta

Only after paid reports repeat:

- selective backend or operator-run live checks;
- scheduled monitoring for verified links only;
- explicit paid workflow and data retention;
- no dashboard unless repeated users ask for it.

### P3: Platform Expansion

Later only:

- WordPress plugin;
- Chrome extension;
- Telegram opt-in bot;
- affiliate-network-specific modules;
- replacement suggestions;
- API;
- team dashboard.

## 8. Hard Non-Goals

P0 explicitly excludes:

- SaaS dashboard;
- public crawler;
- public Telegram scraping;
- joining groups/channels without explicit opt-in;
- Chrome extension;
- WordPress plugin;
- bulk cold email;
- proxy rotation;
- user-agent spoofing;
- CAPTCHA solving;
- rate-limit evasion;
- automatic link replacement;
- AI final verdicts;
- legal/compliance certification;
- "100% accurate" claims;
- exact revenue-loss claims.

## 9. User Workflow

1. User opens the KikuAI hub tool page.
2. User drops a CSV, HTML, or Markdown file, or pastes content.
3. Browser parses the file locally.
4. Tool maps URL-like columns or extracts links.
5. Tool runs deterministic local rules.
6. User sees:
   - total links;
   - commercial/recommendation-looking links;
   - affiliate/tracking-looking links;
   - duplicates;
   - malformed or unsupported URLs;
   - high-risk links needing verification;
   - source/context quality warnings.
7. User downloads a local report.
8. Tool optionally offers a non-payment interest path for a later verified report.

No account, upload, backend, live fetch, or payment is required in P0.

## 10. Input Contract

Primary CSV path:

```csv
url
```

Recommended CSV columns:

```csv
url,source_url,anchor_text,context,notes
```

Accepted URL aliases:

- `url`
- `link`
- `href`
- `target_url`
- `original_url`
- `destination`

Accepted source/context aliases:

- `source_url`
- `page_url`
- `source`
- `source_reference`
- `anchor_text`
- `anchor`
- `text`
- `context`
- `source_context`
- `description`
- `notes`

Secondary inputs:

- HTML: parse uploaded or pasted content and extract `a[href]` links with visible anchor text where available.
- Markdown: extract `[anchor](url)` links and bare HTTP(S) URLs.
- JSONL/NDJSON: optional if the hub implementation can support it without slowing P0.

Unsupported in P0:

- binary office files;
- PDFs as primary input;
- screenshots;
- authenticated exports with unclear provenance;
- public Telegram scraping dumps;
- mixed-provenance files without source context.

## 11. Output Report

P0 report sections:

- summary counts;
- commercial-link inventory;
- affiliate/tracking parameter inventory;
- high-risk links to verify;
- malformed and unsupported URLs;
- duplicate destinations;
- missing or weak source context;
- what this report did not verify;
- recommended next action.

Every finding should include:

- `finding_id`
- `rule_id`
- `severity`
- `confidence`
- `finding_type`
- `url`
- `normalized_url`
- `source_url`
- `anchor_or_context`
- `evidence`
- `recommended_action`

Report formats:

- on-page preview;
- Markdown download;
- HTML download;
- CSV download;
- JSON/JSONL download if easy.

## 12. Finding Buckets

Use three top-level buckets:

- `invalid`: deterministic local problem, such as malformed URL or unsupported scheme.
- `inventory_only`: useful classification, such as affiliate parameter, tracking parameter, marketplace host, app-store URL, or duplicate.
- `needs_verification`: cannot be confirmed locally, but should be reviewed manually or in a paid verified check.

Do not use `broken` as a P0 output bucket except for deterministic local syntax failures. A real remote broken-link claim requires live evidence and/or human verification outside the browser-only P0.

## 13. Initial Rulebook

Deterministic P0 rules:

- malformed URL;
- unsupported scheme;
- duplicate exact URL;
- duplicate normalized destination;
- missing source context;
- affiliate/referral parameter detection;
- campaign/tracking parameter detection;
- marketplace host family detection;
- shortener or redirector host detection;
- suspicious redirector path/query pattern;
- app-store or software marketplace URL detection;
- commercial anchor/context language;
- too many context-free links.

Rules to avoid:

- do not infer product unavailability from URL shape;
- do not infer geo-blocking from URL shape;
- do not strip affiliate/tracking parameters by default;
- do not treat shorteners as broken;
- do not classify `403`, `429`, CAPTCHA, login, timeout, or geo effects in the browser-only path;
- do not let AI decide a final issue verdict.

## 14. Data Model

Core row:

```text
row_id
input_source
input_format
source_url
anchor_text
context
original_url
normalized_url
host
registered_domain
finding_bucket
finding_type
rule_id
severity
confidence
evidence
recommended_action
created_at
extras_json
```

Optional later verified-report fields:

```text
issue_id
page_url
target_url
redirect_chain
observed_status
checked_at
screenshot_or_evidence_path
manual_review_status
reviewer_note
```

## 15. Technical Approach

P0 should be implemented as a static browser-local module inside the KikuAI hub.

Suggested components:

- `FileInput`: drag/drop, paste box, file-type detection.
- `CsvParser`: flexible header mapping and row validation.
- `HtmlParser`: uploaded HTML anchor extraction.
- `MarkdownParser`: Markdown link and bare URL extraction.
- `UrlNormalizer`: deterministic URL parsing, normalization, and dedupe key generation.
- `RuleEngine`: local rules and finding generation.
- `ReportBuilder`: metrics, report sections, and export formats.
- `ToolView`: upload state, findings table, downloads, and next-action CTA.

Implementation requirements:

- run parsing in a Web Worker if files can be large;
- cap file size and row count visibly;
- never fetch third-party URLs in P0;
- never send raw URLs to analytics;
- keep rules test-backed;
- keep all report claims traceable to a rule and source row.

## 16. OSS And Dependency Direction

Prefer lightweight permissive dependencies:

- Markdown parsing: `micromark` or a smaller parser if enough.
- HTML parsing: `parse5`, `linkedom`, or native `DOMParser` if acceptable.
- URL parsing: browser `URL` API plus careful normalization.
- Domain grouping: `tldts` or `psl`.
- CSV parsing: a small well-maintained parser if the hub does not already have one.

Avoid:

- crawler frameworks in P0;
- GPL dependencies in the core path unless intentional;
- generic link-checker CLIs as embedded product logic;
- heavyweight DOM emulation where native browser parsing is enough.

## 17. AI Boundary

No AI is required for P0.

Safe later AI uses:

- report summary drafting;
- grouping similar rows;
- explaining rule categories;
- optional local-model context classification.

Unsafe AI uses:

- final broken/unavailable verdict;
- legal/compliance verdict;
- revenue-loss estimate;
- outreach personalization from raw links;
- automatic rule mutation.

If AI is added later, it must be opt-in and the UI must clearly disclose whether raw link data leaves the user's machine.

## 18. Privacy, Trust, And Legal Boundaries

Safe P0 claims:

- local-first;
- no account required;
- no upload in the free workflow;
- no backend analysis in the free workflow;
- no AI dependency;
- no live third-party fetch;
- ambiguous issues stay ambiguous;
- report is operational guidance, not legal advice.

Dangerous claims:

- SOC2 compliant;
- GDPR compliant;
- enterprise-grade secure;
- legally compliant;
- 100% accurate;
- zero false positives;
- exact lost revenue;
- nothing ever leaves your device if analytics, payments, email, or hosted reports are present.

Before paid reports:

- add privacy policy;
- add terms/scope statement;
- add data retention and deletion wording;
- add refund/rework policy;
- clearly state what, if anything, leaves the user's machine.

## 19. Competitor Context

Current research shows the category is crowded:

- generic broken-link tools and browser extensions are free or cheap;
- affiliate monitors already sell live checks and alerts;
- WordPress plugins already own install-based link management;
- SEO suites already own broad audit workflows.

P0 should not claim to beat these tools at their own jobs.

The wedge is:

- local-first;
- no setup;
- no upload;
- monetized/recommendation-link context;
- conservative evidence;
- proof-before-platform.

Current competitor and pricing claims are snapshots from the research sprint and must be re-verified before public marketing copy.

## 20. Cost And Infrastructure

P0 operating cost should be close to zero:

- static hosting only;
- user device does analysis;
- no backend compute;
- no database;
- no LLM calls;
- no live-check infrastructure.

Cost risks begin with:

- hosted uploads;
- live verification;
- screenshot capture;
- geo checks;
- LLM summaries over raw links;
- manual verified reports.

The main validation cost is manual QA time after P0, not compute.

## 21. Acceptance Criteria

P0 is acceptable when:

- CSV with a single `url` column produces a report.
- CSV with `source_url`, `anchor_text`, `context`, and `notes` preserves those fields.
- HTML import extracts links without network fetches.
- Markdown import extracts Markdown links and bare HTTP(S) URLs.
- Malformed URLs are detected deterministically.
- Unsupported schemes are separated from HTTP(S) URLs.
- Duplicates are detected.
- Affiliate/tracking-looking links are inventoried.
- Marketplace, shortener, redirector, and app-store families are detected as `needs_verification` or `inventory_only`.
- Report clearly states that it did not perform live verification.
- No third-party URL fetch is required.
- No AI dependency is required.
- Tests cover parsers, normalization, rules, reporting, and at least one end-to-end fixture.

## 22. Proof Batch Protocol

Around the P0 fixture workflow, run measured proof batches:

1. Collect `100` rights-clean public affiliate/recommendation links from visible commercial pages or owner-provided exports.
2. Use only public pages, provided files, or explicit opt-in sources.
3. Do not scrape public Telegram.
4. Do not bypass robots, login, CAPTCHA, rate limits, or geo restrictions.
5. Run the local analyzer.
6. Manually verify every `needs_verification` candidate that might become a paid-report example.
7. Log false positives, blocked/ambiguous cases, review minutes, and value clarity.

Pass gates:

- at least `100` checked links;
- at least `5` manually confirmed meaningful issues per `100` links;
- false positives `<=20%`;
- blocked/ambiguous cases `<=20%`;
- QA time `<60` minutes per `100` links;
- direct infrastructure/API cost `<$5` per `100` links;
- no spam or outreach required.

If this batch fails, do not add monitoring. Reshape the rulebook, ICP, or product promise.

First executed web-affiliate proof batch ran as an operator proof before the public hub MVP shipped:

- result memo: `docs/research-sprint/first-web-affiliate-proof-batch-results.md`;
- checked links: `100`;
- manually confirmed meaningful issues: `3`;
- blocked or ambiguous: `8`;
- candidate false positives after manual QA: `0`;
- direct cost: `$0`;
- QA time: `15` minutes;
- verdict: reshape source selection and rules before any paid-report promise.

Implication: continue P0 free hub analyzer, but do not launch a paid verified-report offer until a second stronger source hypothesis or owner-provided exports produce repeatable proof.

## 23. Metrics

P0 product metrics:

- files analyzed;
- rows parsed;
- parse failures;
- link count;
- links with source/context;
- findings per bucket;
- report downloads;
- local runtime;
- user-reported usefulness, if collected manually.

Proof-batch metrics:

- checked links;
- candidate findings;
- manually confirmed issues;
- false positives;
- blocked/ambiguous;
- QA minutes;
- direct cost;
- value clarity score;
- requests for verified report;
- paid report attempts, after paid test begins.

Do not log raw user URLs to remote analytics in P0.

## 24. QA Plan

Fixture coverage:

- minimal CSV with `url`;
- CSV with aliases;
- CSV with missing URL column;
- malformed URLs;
- unsupported schemes;
- duplicates with fragments;
- affiliate query parameters;
- tracking query parameters;
- marketplace domains;
- shorteners;
- redirector-looking paths;
- HTML with body links, nav links, and empty anchors;
- Markdown links and bare URLs;
- large file cap;
- report export snapshots.

Human QA for proof batch:

- confirm source context;
- confirm target URL;
- verify the evidence;
- classify issue type;
- record confidence;
- reject ambiguous results;
- record review minutes.

## 25. Kill Criteria

Park or reshape if:

- users do not bring real files;
- local reports feel like generic broken-link output;
- `needs_verification` is too noisy to be useful;
- proof batch finds fewer than `5` meaningful confirmed issues per `100` links;
- false positives exceed `20%`;
- blocked/ambiguous cases exceed `20%`;
- manual QA exceeds `60` minutes per `100` links;
- users mainly ask for monitoring before valuing the report;
- distribution requires spam, scraping, or broad cold outreach;
- the privacy promise becomes impossible to explain simply.

## 26. Open Questions

- Which KikuAI hub route/name should this tool use? `[TBD]`
- What file-size and row-count cap should P0 enforce? `[TBD]`
- Should JSONL/NDJSON ship in P0 or wait? `[TBD]`
- Should the first CTA be "download report only" or "request verified report interest"? `[TBD]`
- Which second `100`-link source hypothesis can produce `>=5` confirmed meaningful issues per `100` links without higher ambiguity or QA time? `[TBD]`
- Should the tool include synthetic sample files on the page? `[TBD]`

## 27. Recommended Next Implementation Task

Create the KikuAI hub drop-in implementation plan:

1. Map existing KikuAI hub structure and route conventions.
2. Define the local analyzer module boundary.
3. Add fixture files.
4. Implement CSV path first.
5. Add HTML/Markdown import.
6. Add deterministic rule engine.
7. Add report builder.
8. Add tests and screenshot/browser QA.

Do not implement live verification, payment, monitoring, outreach, or Telegram in this task.
