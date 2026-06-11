# Open-Source And GitHub Solution Research

## Executive Verdict
Your MVP is not competing with "broken link checking" as a category. It is competing with generic checkers, SEO crawlers, and WordPress/plugin ecosystems while trying to stay rights-clean, local-first, and human-verified. Given the constraints in [README.md](../../README.md) and [the PRD](../../docs/affiliate-revenue-link-health-mvp-prd.md), the best move is to borrow parsing, normalization, and generic link-validation behavior from OSS, then build your own evidence workflow, QA loop, and monetized-link semantics.

I did not surface a mature open-source affiliate-link monitor that matches the commercial tools in your PRD. That absence is the opportunity.

## OSS map table

| Category | OSS examples | What they do well | License / activity snapshot | Fit for your MVP |
| --- | --- | --- | --- | --- |
| Generic link checkers | [lychee](https://github.com/lycheeverse/lychee), [linkchecker](https://github.com/linkchecker/linkchecker), [markdown-link-check](https://github.com/tcort/markdown-link-check), [html-proofer](https://github.com/gjtorikian/html-proofer) | Check links in Markdown, HTML, and full sites; some handle redirects, headers, retries, robots, auth, and output formats | `lychee`: Apache-2.0/MIT, 3.7k stars, 63 releases, latest 2026-05-01. `linkchecker`: GPL-2.0, 1.1k stars, 11 releases, latest 2025-07-28. `markdown-link-check`: ISC, 701 stars, 27 releases, latest 2025-11-19. `html-proofer`: MIT, 1.6k stars, 77 releases, latest 2026-03-29 | Use as references or external CLIs, not as the product core |
| Parser stack | [micromark](https://github.com/micromark/micromark), [parse5](https://github.com/inikulin/parse5), [cheerio](https://github.com/cheeriojs/cheerio), [linkedom](https://github.com/WebReflection/linkedom), [jsdom](https://github.com/jsdom/jsdom) | Markdown tokenization, HTML parsing, selector-based extraction, DOM-like parsing | Mostly MIT; `linkedom` is ISC. `jsdom`: 21.6k stars, 328 releases, latest 2026-04-30. `cheerio`: 30.4k stars, 62 releases, latest 2026-01-23. `parse5`: 3.9k stars, 51 releases, latest 2026-04-19. `micromark`: 2.2k stars, 118 releases, latest 2025-02-27 | Good building blocks. Prefer the lightest parser that solves the input you actually have |
| URL normalization / domain parsing | [normalize-url](https://github.com/sindresorhus/normalize-url), [whatwg-url](https://github.com/jsdom/whatwg-url), [tldts](https://github.com/remusao/tldts), [psl](https://github.com/lupomontero/psl) | Canonicalization, WHATWG URL parsing, registrable-domain extraction, public suffix handling | All permissive. `normalize-url`: MIT, 877 stars, 28 releases, latest 2026-05-20. `whatwg-url`: MIT, 413 stars, 55 releases, latest 2026-02-18. `tldts`: MIT, 750 stars, 372 releases, latest 2026-05-30. `psl`: MIT, 436 stars, 15 releases, latest 2024-12-02 | Strong fit. This is the safest OSS layer to reuse |
| SEO crawler frameworks | [apache/nutch](https://github.com/apache/nutch), [yasserg/crawler4j](https://github.com/yasserg/crawler4j), [gocolly/colly](https://github.com/gocolly/colly) | Full crawling stacks, robots handling, concurrency, auth, distributed crawling, proxy-oriented collection | `Nutch`: Apache-2.0, 3.2k stars, 3,617 commits. `crawler4j`: Apache-2.0, 4.6k stars, latest release 2018-03-27. `Colly`: Apache-2.0, 25.3k stars, 6 releases, latest 2025-03-27 | Too heavy for a browser-local MVP. Good references for later backend expansion |
| Spec corpora and malformed URL tests | [whatwg/url](https://github.com/whatwg/url), [web-platform-tests/wpt `url/resources/urltestdata.json`](https://github.com/web-platform-tests/wpt/blob/master/url/resources/urltestdata.json) | Canonical URL spec behavior and a large edge-case corpus for parser regressions | `whatwg/url`: 617 stars, 72 issues, 699 commits. `urltestdata.json`: 10,466 lines / 219 KB in WPT | Use as a regression corpus, not as production code |
| Affiliate-specific OSS | None mature surfaced in this quick scan | Generic link tools dominate; commercial affiliate monitoring dominates the niche | N/A | This is the gap your MVP can own |

## Useful libraries
- For Markdown extraction, start with [micromark](https://github.com/micromark/micromark). It is small, current, and designed for Markdown tokenization rather than full-document emulation.
- For HTML parsing, prefer [parse5](https://github.com/inikulin/parse5) as the spec-compliant core, then layer [cheerio](https://github.com/cheeriojs/cheerio) only if selector ergonomics matter more than minimality.
- For DOM-like parsing outside a real browser, [linkedom](https://github.com/WebReflection/linkedom) is the lighter option; [jsdom](https://github.com/jsdom/jsdom) is much heavier and better suited to Node-side test emulation than a browser-local MVP.
- For URL normalization and comparison, use [whatwg-url](https://github.com/jsdom/whatwg-url) for parsing semantics and [normalize-url](https://github.com/sindresorhus/normalize-url) for canonicalization. `normalize-url` explicitly says it is not sanitization, so do not use it as a security boundary.
- For registrable-domain grouping and affiliate-network bucketing, use [tldts](https://github.com/remusao/tldts) or [psl](https://github.com/lupomontero/psl).
- For malformed URL regression tests, seed from [WHATWG URL](https://github.com/whatwg/url) plus [WPT `urltestdata.json`](https://github.com/web-platform-tests/wpt/blob/master/url/resources/urltestdata.json).

## License notes
- Best-fit licenses for your MVP are MIT, Apache-2.0, and ISC. They are low-friction for reuse and embedding.
- [linkchecker](https://github.com/linkchecker/linkchecker) is GPL-2.0. That is the main license constraint in this set. If you want to keep your MVP permissive, portable, or optionally proprietary later, avoid making it a dependency.
- Apache-2.0 is especially safe if you later ship a mixed product, because it is permissive and includes a patent grant.
- `whatwg/url` and WPT are best treated as reference/spec/test material, not as a runtime dependency you embed blindly.
- `normalize-url` is useful for deduplication and comparison, but it does not make untrusted URLs safe.

## Gaps OSS does not solve
- Rights-clean input collection, consent tracking, and deletion/revocation.
- The exact monetized-link semantics you care about, such as stripped tracking, unavailable products, wrong destinations, geo/blocked outcomes, and affiliate-specific edge cases.
- Human QA workflows with screenshots, verdicts, and confidence tracking.
- Buyer-facing reporting that explains why a broken monetized link matters.
- A local-first benchmark and evidence ledger for the `100 + 100` lane test in your PRD.
- Restraint around public Telegram scraping and crawling behavior.

## Build-vs-use recommendation
1. Use OSS for the substrate: Markdown parsing, HTML parsing, URL parsing/normalization, domain grouping, and malformed-URL regression data.
2. Use generic link checkers like [lychee](https://github.com/lycheeverse/lychee) and [markdown-link-check](https://github.com/tcort/markdown-link-check) as references or external validation tools, not as the user-facing product.
3. Build the lane-specific product logic yourself: rights-clean ingest, evidence rows, QA review, issue classification, and report generation.
4. Avoid crawler frameworks like [Nutch](https://github.com/apache/nutch), [crawler4j](https://github.com/yasserg/crawler4j), and [Colly](https://github.com/gocolly/colly) in the browser-local MVP. They solve a larger problem than you need and push you toward crawl-fleet complexity.
5. Avoid GPL dependencies in the core path unless you are intentionally choosing that licensing model.

## GitHub pain evidence links
- [lychee issues](https://github.com/lycheeverse/lychee/issues): [#2117](https://github.com/lycheeverse/lychee/issues/2117) valid fragments with URL-encoded emoji false positive, [#2128](https://github.com/lycheeverse/lychee/issues/2128) valid fragments wrongly flagged, [#2190](https://github.com/lycheeverse/lychee/issues/2190) transient network errors cached indefinitely.
- [markdown-link-check issues](https://github.com/tcort/markdown-link-check/issues): [#553](https://github.com/tcort/markdown-link-check/issues/553) no links found falsely, [#551](https://github.com/tcort/markdown-link-check/issues/551) false positive on `admin.google.com`, [#215](https://github.com/tcort/markdown-link-check/issues/215) improper relative path parsing, [#109](https://github.com/tcort/markdown-link-check/issues/109) DDoS-protected sites marked failed.
- [linkchecker issues](https://github.com/linkchecker/linkchecker/issues): [#912](https://github.com/linkchecker/linkchecker/issues/912) bad input like `https://https://...`, [#895](https://github.com/linkchecker/linkchecker/issues/895) status 426 on `rsync.samba.org`, [#880](https://github.com/linkchecker/linkchecker/issues/880) crawling more than 500,000 URLs, [#853](https://github.com/linkchecker/linkchecker/issues/853) ignored file-size failures not behaving as expected.

## Sources and assumptions
- Local grounding docs: [README.md](../../README.md) and [affiliate-revenue-link-health-mvp-prd.md](../../docs/affiliate-revenue-link-health-mvp-prd.md).
- GitHub metadata and issue lists were sampled on 2026-06-11. Stars, releases, and issue counts are snapshots and may drift.
- I relied on official repo pages, issue lists, and spec/test repositories rather than blog posts or secondary summaries.
- The key interpretation is an inference from your local docs: the MVP is rights-clean, local-first, and explicitly not a crawler fleet or SaaS.