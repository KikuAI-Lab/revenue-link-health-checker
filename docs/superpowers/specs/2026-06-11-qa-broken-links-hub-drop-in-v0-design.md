# QA Broken Links Hub Drop-In V0 Design

Date: 2026-06-11
Status: draft for Nick review

## Decision

The first public version should be a KikuAI hub drop-in tool, not a SaaS,
dashboard, crawler fleet, WordPress plugin, Chrome extension, public Telegram
bot, or bulk outreach system.

V0 is a browser-local file analyzer:

> file in -> local monetized-link risk analysis -> downloadable report out

The tool must not claim live broken-link verification in the browser-only path.
Browser sandboxes, CORS, opaque fetch responses, redirect handling limits, bot
checks, and marketplace behavior make reliable client-side status verification
unavailable for arbitrary third-party URLs.

## Product Boundary

V0 can safely do:

- parse user-supplied files in the browser;
- extract URLs, anchors, nearby context, source-page hints, and query
  parameters;
- classify likely affiliate, marketplace, recommendation, shortener, and
  tracking-link patterns;
- detect malformed URLs, duplicates, suspicious redirects by pattern, missing
  source context, weak evidence, and high-risk link families;
- generate a local HTML/CSV/Markdown-style report;
- invite the user to request a paid verified check if the local report shows
  enough commercial-link surface area.

V0 must not do:

- promise live HTTP status, redirect-chain, or availability verification;
- fetch third-party pages at scale from the browser;
- call AI for final issue verdicts;
- scrape public Telegram sources;
- use proxies, browser-identity spoofing, CAPTCHA solving, or rate-limit
  evasion;
- send outreach or contact site owners.

## Primary Input Contract

Primary test path: CSV.

Minimum required column:

```csv
url
```

Recommended columns:

```csv
url,source_url,anchor_text,context,notes
```

Accepted aliases should be permissive for common exports:

- `url`, `link`, `href`, `target_url`, `original_url`
- `source_url`, `page_url`, `source`, `source_reference`
- `anchor_text`, `anchor`, `text`
- `context`, `source_context`, `description`

CSV is the acceptance path because it is deterministic, easy to test, and maps
well to exports from spreadsheets, crawlers, content audits, CMS plugins, and
manual lists.

## Secondary Inputs

HTML and Markdown import are allowed as best-effort helpers:

- HTML: extract `a[href]` links and visible anchor text from uploaded files.
- Markdown: extract `[anchor](url)` links and bare HTTP(S) URLs.

These parsers must not fetch linked pages. They only inspect the uploaded file.

If HTML/Markdown parsing produces weak context, the report should say so
instead of inventing confidence.

## User Flow

1. User opens the KikuAI hub tool page.
2. User drops a CSV, HTML, or Markdown file.
3. Browser parses the file locally.
4. Tool shows:
   - total links;
   - external commercial/recommendation-looking links;
   - affiliate or tracking-looking links;
   - duplicate destinations;
   - malformed or unsupported URLs;
   - links needing verified live check;
   - report quality warnings.
5. User downloads a local report.
6. If enough value exists, page offers a non-payment interest path for a later
   verified report.

## Analysis Rules

Rules must be deterministic and explainable.

Initial rule families:

- URL validity: missing scheme, invalid host, unsupported schemes, fragments
  without destination.
- Duplicate detection: exact URL duplicates and normalized destination
  duplicates.
- Affiliate/tracking signals: known query parameters, marketplace domains,
  affiliate networks, ref/tag/campaign-like parameters.
- Commercial context signals: anchor/context includes product, review,
  pricing, deal, coupon, buy, best, recommended, alternative, or tool language.
- Marketplace/link-shortener signals: Amazon, AliExpress, app stores, common
  shorteners, redirector domains, tracking networks.
- Evidence quality signals: missing anchor/context/source URL, too many
  context-free links, unsupported file structure.

Each finding must have:

- rule id;
- severity;
- confidence;
- explanation;
- affected URL;
- optional source URL;
- optional anchor/context;
- recommended next step.

## Report Shape

V0 report sections:

- Summary counts.
- Commercial-link inventory.
- High-risk links to verify.
- Duplicates and malformed links.
- Affiliate/tracking parameter inventory.
- Source/context quality warnings.
- What this report did not verify.
- Recommended next action.

The report copy must be conservative:

- say "risk", "needs verification", or "candidate";
- do not say "broken" unless the evidence is local and deterministic, such as
  an invalid URL format;
- do not estimate lost revenue;
- do not imply endorsement from affiliate networks or marketplaces.

## Optional Local AI

No AI is required for V0.

Possible later local-model use:

- classify anchor/context as commercial recommendation vs ordinary link;
- cluster links by product/category;
- draft a plain-language report summary.

AI must not produce final broken/unavailable verdicts. AI output should be
treated as advisory classification only, with deterministic evidence shown
beside it.

## Architecture

V0 should be implemented as a small browser-local module inside the KikuAI hub
surface.

Suggested components:

- `FileInput`: drag/drop and file-type detection.
- `CsvParser`: flexible header mapping and row validation.
- `HtmlParser`: best-effort anchor extraction from uploaded HTML.
- `MarkdownParser`: Markdown links and bare URL extraction.
- `UrlNormalizer`: deterministic URL parsing, normalization, and dedupe keys.
- `RuleEngine`: deterministic local rules and finding generation.
- `ReportBuilder`: summary metrics, table rows, and downloadable report data.
- `ToolView`: upload state, findings table, report download, and next-action
  CTA.

No backend is required for V0.

## Error Handling

The tool should handle:

- empty files;
- unsupported file types;
- CSV with no URL-like column;
- invalid encoding;
- very large files with a visible cap;
- rows with invalid URLs;
- HTML/Markdown files with no extractable links.

Failure states should explain how to fix the input, not ask the user to contact
support.

## Acceptance Criteria

V0 is acceptable when:

- CSV upload with `url` only produces a report.
- CSV upload with recommended columns preserves source and context.
- HTML upload extracts links without network fetches.
- Markdown upload extracts Markdown and bare HTTP(S) links.
- Malformed URLs are reported deterministically.
- Duplicates are detected.
- Affiliate/recommendation-looking links are separated from ordinary links.
- Report clearly says it is not live broken-link verification.
- No third-party URL fetch is required in the browser path.
- No AI dependency is required.
- Tests cover parsers, normalization, rule output, report output, and at least
  one end-to-end sample.

## Open Product Questions

These do not block V0 design, but they should be answered before any paid
launch:

- Should the later paid next step be "verified report request" or "paid export"?
- Should the public page target affiliate site owners, SaaS/tools directories,
  or broader recommendation-page owners first?
- What exact file examples should be included on the hub page?
- Should live verification be a separate backend add-on, a CLI-assisted paid
  fulfillment step, or postponed until real demand appears?

## Recommended Next Step

Write an implementation plan for a hub drop-in V0 with CSV as the primary
acceptance path and HTML/Markdown as best-effort secondary parsers.

Do not implement live verification in the browser-only MVP.

Do not implement payment, paywall, paid export, or paid-report checkout in V0.
The first public MVP is free.
