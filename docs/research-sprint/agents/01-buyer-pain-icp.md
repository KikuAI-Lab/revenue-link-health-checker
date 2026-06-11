# Buyer Pain And ICP Research

## Executive Verdict

Yes, this can become a no-call, self-serve product or a paid report offer, but only if it stays narrow: revenue-link health for affiliate-heavy publishers, not a generic broken-link checker.

Strongest first ICP: Amazon/marketplace roundup publishers and niche affiliate review site owners. They have the clearest recurring pain, the highest urgency, and the easiest self-serve purchase motion. SaaS/tool directory owners and resource-page owners are viable secondary ICPs, but they are less acute and more easily absorbed by generic SEO/link tools.

Repo-real note: the current codebase is a Python 3.11, standard-library-only CLI, and the checker is deterministic URL normalization plus redirect/status/body-marker classification, with ambiguous handling for 401/403/429 and CAPTCHA-like bodies in [`linkhealth/checker.py`](../../linkhealth/checker.py). The browser-local no-upload MVP in your prompt is the strategic target; it is not the current implementation in this repo.

## Ranked ICPs table

| Rank | ICP | Strong recurring job | Urgency trigger | Can pay without procurement? | What they do now | Why they might trust a free browser-local checker | Smallest proof that could make them pay |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Amazon / marketplace roundup publishers and niche affiliate review site owners | Protect commissions on pages that sell products through outbound links | Traffic or revenue drop, broken Amazon links, delisted/out-of-stock products, stripped affiliate tags, redirect changes | Yes. Existing tools already sit in the $19-$39/mo range, with WordPress options at $79-$279 one-time | Manual spot checks, WordPress affiliate plugins, generic SEO suites, CSV imports into link managers | No upload, no login, local-only file handling, raw evidence, explicit “needs live verification” state instead of claiming a link is broken | One free scan of a real money page that surfaces 1-3 high-confidence candidate issues, or 3-5 confirmed issues per 100 links |
| 2 | SaaS/tool directory owners and resource-page owners with commercial recommendations | Keep outbound recommendations current and credible | Sponsor audit, partner changes, migration, content refresh, link rot | Yes, but the pain is usually softer than Amazon-heavy pages | Generic broken-link checkers, CMS plugins, manual page refreshes | Same trust wedge, but they need page-cluster or directory-level reports more than whole-site crawling | One verified issue on a high-value directory or resource page |
| 3 | Opt-in Telegram/AliExpress channel admins, as a comparison lane | Keep deal links alive and current in fast-moving feeds | Offer expiry, product unavailability, broken shortlinks, revenue drop | Yes, but ARPU is usually lower and rights/ingestion constraints are tighter | Manual checks, channel admin exports, platform-native workflows | Only if fully opt-in and consented; any public scraping or dataset building breaks the lane | A batch report showing link availability loss before the offer expires |

## Evidence

- Local repo context is clear: [`README.md`](../../README.md) says the project is a local-first, Python `3.11+`, standard-library-only workflow with no API keys and no AI dependency.
- The checker is conservative by design in [`linkhealth/checker.py`](../../linkhealth/checker.py): it follows redirects, flags 404/410 and persistent 5xx as candidate issues, and marks 401/403/429 and CAPTCHA-like bodies as ambiguous rather than broken.
- [AffilGuard](https://affilguard.io/) currently positions itself as affiliate link monitoring with 20 links free forever, no credit card required, daily or hourly checks, 60+ networks, and a $19/month Pro plan.
- [PageRadar’s affiliate link checker](https://pageradar.io/features/affiliate-link-checker) currently offers a free live test with no signup, geo-targeted monitoring from 167 countries, and pricing from €39/month.
- [AMZ Watcher pricing](https://amzwatcher.com/pricing/) currently positions the product around broken Amazon links, missing affiliate tags, and low-quality products; it offers a free broken links report and says checks can run every 1, 3, 5, 7, 14, or 28 days.
- [Lasso pricing](https://getlasso.co/pricing/) currently bundles broken link alerts into paid tiers; the free plan does not include them, and paid tiers start at $19/month.
- [ThirstyAffiliates pricing](https://thirstyaffiliates.com/pricing) currently includes an Automatic 404 Checker and Link Event Notification Emails in paid tiers; annual pricing is shown around $99.60, $149.60, and higher tiers.
- [BetterLinks pricing](https://betterlinks.io/pricing/) currently includes a Broken Links Checker, with pricing shown at $79, $187, and $279.
- [Ahrefs’ broken link checker](https://ahrefs.com/broken-link-checker) shows that generic broken-link checking is already commoditized inside a broader SEO suite with scheduled crawls and link-building content around broken pages.

## Assumptions

- Exact willingness to pay for a browser-local, no-upload report versus a monitoring subscription is [TBD: verify].
- The relative conversion strength of Amazon-heavy publishers versus SaaS/tool directories versus resource pages is [TBD: verify].
- Public vendor claims like “15-30% of affiliate links break within a year” on AffilGuard are marketing claims, not independently verified benchmark data.
- Exact search-intent volume for “affiliate link checker,” “broken Amazon links,” and “resource page link audit” is [TBD: verify].
- The best first price point for a paid report is [TBD: verify], but current competitor pricing suggests a one-off report can plausibly sit below existing subscriptions and plugins.

## Strongest first ICP

Amazon/marketplace roundup publishers and niche affiliate review site owners are the best first buyers.

Why this segment wins:
- Their pain is directly tied to commission loss, not just cleanliness or SEO.
- The trigger is recurring and concrete: delisted products, broken Amazon links, missing tags, changing redirect flows, and unavailable products.
- They already pay for adjacent tools, so a paid report is believable without procurement.
- They can understand a browser-local trust story immediately: no upload, no crawler farm, no backend, just their own file and a conservative report.

Best first offer:
- A free local scan that produces a conservative report.
- A paid one-off “revenue-link health report” for one site or content cluster.
- Only after that should you test monitoring.

Distribution path:
- Inbound search intent plus creator/affiliate communities, not cold outreach.
- Target high-intent queries and page types first: affiliate link checker, broken Amazon links, broken affiliate links, and resource-page link audit.
- If you later test Telegram, do it only through opt-in admin-led pilots, not public scraping.

## Kill Criteria

- If rights-clean scans of real money pages do not routinely surface at least 3 confirmed issues per 100 links.
- If false positives or blocked/ambiguous results exceed the current 20% guardrail in realistic samples.
- If users treat this as generic SEO broken-link checking only, because that space is already crowded and cheap.
- If the only credible buyer motion requires sales calls or procurement.
- If the browser-local trust wedge does not materially outperform existing free previews, plugins, or subscriptions.

## Recommended Next Experiment

Run a tiny, rights-clean proof test on public affiliate-heavy pages only:

1. Pick 10 public pages with visible commercial recommendations.
2. Produce local-only CSV/HTML/Markdown scans and a one-page report per page.
3. Show the report to a small set of opt-in operators or publicly reachable site owners.
4. Test one paid offer first: a one-off report at a low, self-serve price point.
5. Measure whether the response is “nice tool” or “show me the report for my site.”

If you want, I can turn this into a tighter buyer memo with a sharper pricing recommendation and a landing-page angle next.