# GitHub Tool Scout: KikuAI Drop-In Link/File Repair

Date: 2026-06-16

## Scope

Bounded GitHub and package-registry pass for open-source projects that could strengthen a KikuAI browser-local, drop-in, same-window link/file repair product.

The current product constraint is strict: prefer local parsing, local diagnosis, local repair/export, minimal user steps, no bulk crawler/dashboard posture for the first MVP.

## Main Finding

The strongest OSS surface is not "affiliate link checker" repos. That search space is thin and mostly unmaintained or toy-sized. The useful leverage is in mature generic link checkers, HTML/Markdown parsers, file-format parsers, and URL/domain extraction libraries.

## Strong Candidates

| Tool | Type | Signals | Fit | Main limit | Source |
| --- | --- | --- | --- | --- | --- |
| lychee | Rust CLI link checker | 3.7k stars, Apache-2.0, pushed 2026-06-16 | Excellent benchmark/reference engine for local corpus tests and CLI/server mode | Not browser-drop-in friendly without extra packaging | https://github.com/lycheeverse/lychee |
| linkinator | TypeScript/Node link checker | 1.2k stars, MIT, npm 7.6.1, modified 2026-02-27 | Best Node-side candidate for evaluation harness and optional API/CLI status checks | Browser hub cannot freely check arbitrary URLs because of CORS | https://github.com/JustinBeckwith/linkinator |
| muffet | Go website link checker | 2.6k stars, MIT, pushed 2026-06-16 | Good crawler prior art and performance reference | Go binary; less useful inside Nuxt/browser-local MVP | https://github.com/raviqqe/muffet |
| parse5 | HTML parser/serializer | 3.9k stars, MIT, npm 8.0.1, modified 2026-04-19 | Strong base for dropped HTML parsing and exact href replacement/export | Lower-level AST work required | https://github.com/inikulin/parse5 |
| rehype | HTML processor | 2.2k stars, MIT, npm 13.0.2 | Good if we want plugin-style HTML transformations | More abstraction than parse5; only use if transformations grow | https://github.com/rehypejs/rehype |
| remark | Markdown processor | 8.9k stars, MIT, npm 15.0.1 | Strong base for dropped Markdown/resource-page repair | Plugin pipeline can be heavier than a narrow parser | https://github.com/remarkjs/remark |
| micromark | Markdown parser | 2.2k stars, MIT, npm 4.0.2 | Smaller parser option with positional info | Lower-level than remark for mutation/export | https://github.com/micromark/micromark |
| linkifyjs | Plain-text URL extraction | 2.0k stars, MIT, npm 4.3.3, modified 2026-05-13 | Useful for CSV/TXT/pasted text URL discovery | Not enough alone for structured document repair | https://github.com/nfrasser/linkifyjs |
| tldts | Domain/public-suffix parser | 751 stars, MIT, npm 7.4.3, modified 2026-06-15 | Useful for grouping, merchant/domain classification, dedupe | Not a checker or parser by itself | https://github.com/remusao/tldts |
| pdf.js | Browser PDF parser/renderer | 53k stars, Apache-2.0, npm pdfjs-dist 6.0.227 | Future PDF input extraction if user demand appears | Heavy; exact PDF repair/export is hard | https://github.com/mozilla/pdf.js |
| mammoth.js | DOCX to HTML/Markdown | 6.2k stars, BSD-2-Clause, npm 1.12.0 | Future DOCX resource-page link extraction | Conversion can lose exact Word formatting; repair/export needs care | https://github.com/mwilliamson/mammoth.js |
| JSZip | ZIP read/write | 10k stars, dual MIT/GPL, npm 3.10.1 | Useful for Office/XML bundles and browser-local zipped artifacts | License/options should be reviewed before embedding | https://github.com/Stuk/jszip |
| SheetJS/xlsx | Spreadsheet parser/writer | 36k stars, Apache-2.0, npm 0.18.5 | Future CSV/XLSX affiliate-link inventory import/export | GitHub repo notes a new home; verify upstream/current package before depending | https://github.com/SheetJS/sheetjs |

## Lower-Priority Or Avoid For Now

| Tool | Reason |
| --- | --- |
| stevenvachon/broken-link-checker | Good historical JS project, but npm package was last modified in 2022; linkinator is a better current Node choice. |
| Check-My-Links Chrome extension | Useful prior art for P2/P3 extension mode, but it pushes the product toward extension workflow, which is not P0. |
| Affiliate-specific GitHub repos | Searches for affiliate/AliExpress/Telegram-specific checkers returned mostly zero-star, old, or toy projects. Not enough to build on. |
| is-url-online | Browser/server status helper, but npm last modified 2022; avoid unless a narrow test proves it solves a real CORS/status issue. |
| robots-parser | Could be useful in server/CLI crawler mode, but not relevant to browser-local P0. |

## Product Implications

1. The next MVP should strengthen the "drop file -> parse -> show actionable repair/result -> export patched file" loop, not become a crawler dashboard.
2. For public hub P0, do not promise live HTTP status verification for arbitrary external URLs unless there is a server/CLI/extension mode. Browser CORS will create false negatives and confusing failures.
3. The highest-leverage browser-local upgrade is a structured extractor/patcher stack:
   - HTML: parse5 first; rehype only if transformations become plugin-like.
   - Markdown: remark first; micromark only if we need lower-level position control.
   - TXT/CSV/pasted text: linkifyjs plus URL/domain normalization.
   - Domain grouping/classification: tldts.
4. Use lychee/linkinator as evaluation baselines, not necessarily as embedded product engines.
5. If users want "check my live page" rather than "fix my dropped file", the honest later path is one of:
   - local CLI runner,
   - browser extension,
   - optional API/worker with clear privacy language and rate limits.

## Recommended Next Experiment

Build a tiny `link-document-doctor` prototype for dropped HTML and Markdown:

- Parse file locally.
- Extract all links with page/file context.
- Classify obvious issues without network: empty href, mailto/tel weirdness, duplicate tracking params, malformed URLs, non-HTTPS commercial links, affiliate tag presence/missingness where rules are deterministic.
- Let the user replace a URL inline.
- Export the patched file.
- Run a benchmark against 10 real public examples and compare extraction count against `linkinator` or `lychee` where applicable.

Success condition: the user gets a patched artifact, not only a count of bad links.

## Notes

GitHub search hit a secondary rate limit near the end of the pass, after the strongest candidates were already collected. Treat the "WASM/browser link checker" niche as not fully exhausted, but no strong candidate surfaced in web fallback search.
