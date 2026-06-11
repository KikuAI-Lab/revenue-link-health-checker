# Data Surface And Schema Research

## Executive Verdict
Repo-real baseline: this repo is a Python `3.11+`, stdlib-only package at `0.1.0`, and the current loader accepts only `CSV` or `JSONL/NDJSON` inputs with six required columns and two supported lanes (`telegram_aliexpress`, `web_affiliate`). `original_url` must be an absolute `http(s)` URL. See [pyproject.toml](../../pyproject.toml#L5), [linkhealth/io.py](../../linkhealth/io.py#L20), and [linkhealth/models.py](../../linkhealth/models.py#L8).

For the browser-local MVP, the practical next support is:

1. row-based manifests first: `CSV` and `JSONL` as the canonical ingest layer
2. export-derived rows next: WordPress `XML/WXR`, Screaming Frog `CSV/XLS/XLSX/Google Sheets`, BetterLinks `CSV`, Ahrefs report `CSV`
3. list-like surfaces next: `sitemap.xml`, URL lists, pasted HTML, pasted Markdown
4. opt-in Telegram/AliExpress admin exports last, and only when rights-clean

This is aligned with the repo’s own P0 framing: opt-in AliExpress/Telegram links plus public affiliate/recommendation pages, not a generic broken-link checker. See [README.md](../../README.md#L3) and [docs/affiliate-revenue-link-health-mvp-prd.md](../../docs/affiliate-revenue-link-health-mvp-prd.md#L13).

## Supported Input Surfaces Ranked
| Rank | Surface | What users can already export/provide | Common columns / fields | Support recommendation |
|---|---|---|---|---|
| 1 | CSV manifests | Native CSV from tools or hand-built row lists | URL, source URL, title/context, status, notes | First-class V1; lowest friction |
| 2 | JSONL/NDJSON manifests | Easy for browser-local workflows and test fixtures | Same as CSV, plus nested extras | First-class V1 canonical format |
| 3 | WordPress exports | WordPress exports as XML/WXR | posts, pages, custom post types, comments, custom fields, categories, tags, taxonomies, users | Support via normalizer |
| 4 | Screaming Frog exports | CSV, Excel 97-2004, Excel Workbook, Google Sheets; list mode can paste/upload URL lists; XML sitemap output | URL, response codes, redirects, inlinks/outlinks, canonicals, titles, directives, sitemap attrs | High priority; strong fit for crawl-derived rows |
| 5 | BetterLinks / link-manager exports | CSV export of links, analytics, settings, or all data; keyword rule CSV | keywords, shortened URL, post types, categories, tags, open new tab, nofollow, boundaries, status | High priority for affiliate/link-manager users |
| 6 | Ahrefs reports | Ahrefs says any report can be exported as CSV | report-dependent; generally URL, backlinks, anchors, status fields | Support as generic CSV import, not Ahrefs-specific parsing |
| 7 | Google Search Console downloads | Report data download from performance reports | queries, pages, countries, devices, search appearance, dates; clicks, impressions, CTR, average position | Support as a source of page/query lists, not as the core schema |
| 8 | HTML / Markdown pasted pages | User-pasted page text, CMS exports, newsletter archives, docs | `href`, anchor text, surrounding text, headings, rel attrs | Good for browser-local extraction |
| 9 | Sitemap / page lists | `sitemap.xml`, URL lists, plain text lists | URLs, `lastmod`, `changefreq`, `priority` | Support as a lightweight discovery surface |
| 10 | Opt-in Telegram / AliExpress collections | Admin-provided exports or explicit opt-in bot feeds only | original URL, post reference, channel/group reference, consent basis | Support only when rights-clean |

## Recommended V1 Input Schema
Keep the core small and normalize everything else into optional metadata.

### Required core
- `sample_id`
- `lane` (`web_affiliate` or `telegram_aliexpress`)
- `original_url`
- `source_reference`
- `source_context`
- `consent_basis` for `telegram_aliexpress` rows

### Optional enrichment
- `source_format` (`csv`, `jsonl`, `xml`, `html`, `markdown`, `txt`)
- `source_type` (`wordpress_export`, `screaming_frog_export`, `betterlinks_export`, `gsc_export`, `sitemap`, `pasted_html`, `pasted_markdown`, `telegram_opt_in_export`)
- `source_title`
- `page_title`
- `anchor_text`
- `network`
- `post_type`
- `category`
- `tag`
- `status_code`
- `final_url`
- `redirect_hops`
- `canonical_url`
- `nofollow`
- `published_at`
- `lastmod`
- `notes`
- `extras_json`

Pragmatically, V1 should accept vendor-specific columns as aliases, then preserve the unknown leftovers in an `extras_json` blob instead of trying to hard-code every exporter.

## Header Alias Map
Canonical -> common aliases seen in exports or likely user input:

- `sample_id` -> `id`, `row_id`, `sample`, `sampleId`
- `lane` -> `lane`, `surface`, `source_type`, `input_type`
- `original_url` -> `url`, `link`, `destination`, `target_url`, `href`
- `source_reference` -> `source`, `source_url`, `page_url`, `post_url`, `export_file`, `sitemap_url`
- `source_context` -> `context`, `title`, `page_title`, `anchor_text`, `query`, `keyword`, `label`, `note`
- `consent_basis` -> `consent`, `permission`, `opt_in`, `provenance`, `admin_export`
- `network` -> `affiliate_network`, `program`, `merchant`, `vendor`
- `status_code` -> `status`, `http_status`, `response_code`
- `final_url` -> `resolved_url`, `destination_url`
- `canonical_url` -> `canonical`
- `redirect_hops` -> `redirects`, `hop_count`
- `lastmod` -> `modified`, `updated_at`, `last_modified`
- `page_title` -> `title`, `post_title`
- `anchor_text` -> `link_text`, `keyword`, `label`
- `published_at` -> `date`, `published`, `created_at`
- `source_format` -> `format`, `file_type`
- `source_type` -> `surface`, `export_type`

## 10 Realistic Example Rows
Synthetic fixtures only. These are rights-clean because they use placeholder domains and invented labels.

```csv
sample_id,lane,consent_basis,source_reference,source_context,original_url,source_format,source_type
wp-001,web_affiliate,public_page,wordpress_export_2026-06-11.xml,"WordPress export; post title: 2026 camera guide",https://merchant.example/product/camera-7,xml,wordpress_export
sf-001,web_affiliate,public_page,screaming_frog_2026-06-11.csv,"Screaming Frog list-mode row; source page: /guides/gear",https://merchant.example/product/lens-50,csv,screaming_frog_export
bl-001,web_affiliate,public_page,betterlinks_export_2026-06-11.csv,"BetterLinks export; keyword: best travel tripod",https://merchant.example/tripod-compact,csv,betterlinks_export
gsc-001,web_affiliate,public_page,gsc_performance_2026-06-11.csv,"Search Console query export; query: best travel tripod",https://example.com/reviews/travel-tripods,csv,gsc_export
sm-001,web_affiliate,public_page,sitemap.xml,"Sitemap URL list; lastmod 2026-06-01",https://example.com/articles/gift-guide,xml,sitemap
html-001,web_affiliate,public_page,https://example.com/newsletter/archive/june,"Pasted HTML fragment with one outbound affiliate link",https://merchant.example/deal?utm_source=newsletter,html,pasted_html
md-001,web_affiliate,public_page,https://example.com/editorial/links.md,"Pasted Markdown list of curated recommendations",https://merchant.example/headphones?ref=site,markdown,pasted_markdown
rep-001,web_affiliate,public_page,affiliate_report_q2_2026.csv,"Affiliate report export; niche: camera accessories",https://merchant.example/product/adapter-2,csv,affiliate_report
tg-001,telegram_aliexpress,admin_export_2026-06-01,approved-channel-a,"Telegram admin export; post 481; opt-in monitoring",https://s.click.aliexpress.com/e/_Dexample,csv,telegram_opt_in_export
tg-002,telegram_aliexpress,admin_export_2026-06-01,approved-group-b,"Telegram bot-added source; post 1092; opt-in monitoring",https://s.click.aliexpress.com/e/_Eexample,jsonl,telegram_opt_in_export
```

## Unsupported / Unsafe Surfaces
- Public Telegram scraping
- Joining private Telegram groups/channels without explicit opt-in
- Any authenticated surface where the user has not provided rights-clean exports
- CAPTCHA bypass, proxy rotation, identity spoofing, or rate-limit evasion
- PDF or screenshot-only sources as the primary input format
- Binary office formats and macro-heavy files as a first-class ingest target
- Vendor dashboards that do not expose row-level URLs or row-level evidence
- Mixed-provenance spreadsheets with no clear source URL or export origin
- “Download everything” corpus-building from public pages for training or enrichment

## Fixture Ideas For Tests
- `wordpress_export.xml` with 2 posts, 1 page, and 2 outbound links
- `screaming_frog_urls.csv` with `url`, `status_code`, `final_url`, `inlinks`, `outlinks`
- `betterlinks_export.csv` with keyword rules, nofollow, post types, categories, and status
- `gsc_performance.csv` with query/page rows and clicks/impressions/CTR/position
- `sitemap.xml` with 3 URLs and `lastmod`
- `page.html` with a few `<a>` tags, one broken relative link, one affiliate link
- `page.md` with markdown links and one bare URL
- `telegram_opt_in.csv` with `source_reference`, `post_id`, `consent_basis`, and `original_url`
- `alias-mapping.csv` to test vendor header normalization
- `mixed-surfaces.jsonl` to verify the parser ignores extra fields but preserves core required fields

## Evidence vs Assumptions
### Verified
- WordPress exports are XML/WXR and include posts, pages, custom post types, comments, custom fields, categories, tags, taxonomies, and users. [WordPress.org docs](https://wordpress.org/documentation/article/tools-export-screen/)
- Screaming Frog exports can be CSV, Excel 97-2004 Workbook, Excel Workbook, or Google Sheets; it also supports list mode and XML sitemap output. [Screaming Frog docs](https://www.screamingfrog.co.uk/seo-spider/user-guide/general/)
- BetterLinks exports data as CSV and its auto-link keyword export includes columns such as keywords, shortened URL, post types, categories, tags, open new tab, nofollow, and status. [BetterLinks export docs](https://betterlinks.io/docs/export-data-betterlinks/) and [BetterLinks CSV format docs](https://betterlinks.io/docs/auto-link-keywords-import-export-betterlinks/)
- Google Search Console performance reports group by queries, pages, countries, devices, search appearance, and dates, and expose clicks, impressions, CTR, and average position; the help doc says many reports have an export button. [Search Console help](https://support.google.com/webmasters/answer/7576553?hl=en)
- Ahrefs says any report can be exported as CSV. [Ahrefs broken link checker page](https://ahrefs.com/broken-link-checker)

### Assumptions / Inferences
- Search Console’s help page confirms downloadable report data but does not spell out a specific file extension in the text I verified, so I treat it as a spreadsheet-style export rather than asserting a single exact MIME type.
- The recommended canonical schema is an inference from the repo’s current six-field contract plus common columns across the verified exports; it is not a vendor standard.
- HTML/Markdown support is a parser recommendation, not a documented exporter claim.
- Telegram/AliExpress support should remain opt-in/admin-provided only; that is a product/legal constraint from the PRD, not a public export standard.

If you want, I can turn this into a concrete import contract next: header names, type rules, and parser precedence for each surface.