# First Web-Affiliate Proof Batch Results

Date: 2026-06-11
Status: executed, manual QA complete
Decision: reshape source selection and rules before any paid-report promise

## Summary

Nick approved operator-selected public sources for the first web-affiliate proof batch. The batch checked `100` rights-clean public affiliate/recommendation links from `6` public pages and manually reviewed every automated candidate issue.

Result: the problem is real, but this source mix did not pass the first proof gate.

- Checked links: `100`
- Automated candidate issues: `3`
- Manually confirmed issues: `3`
- Confirmed issues per `100` links: `3`
- Gate: `>=5` confirmed meaningful issues per `100` links
- Blocked or ambiguous results: `8`
- Candidate false positives after manual QA: `0`
- Operator-recorded manual QA time: `15` minutes
- Direct infrastructure/API cost: `$0`

This supports the free hub drop-in analyzer direction, but it does not yet justify a paid verified report as a repeatable offer from broad self-selected public pages.

## Evidence Used

Local run artifacts are intentionally ignored and not committed. The run directory was `.local/proof-batch-2026-06-11/` and contained normalized samples, live-check evidence, QA decisions, manual browser checks, metrics, and the generated lane report.

Public source pages used in the final `100`-link sample:

| source | rows used | notes |
| --- | ---: | --- |
| [AI and Realtors](https://aiandrealtors.com/) | 13 | public recommendation page |
| [Outdoors.com Amazon gear roundup](https://outdoors.com/outdoor-gear-i-brought-to-the-amazon/) | 9 | public affiliate/recommendation article |
| [TechGearLab tools category](https://www.techgearlab.com/topics/tools/best-tools) | 40 | public product-review/category page |
| [Dear Blogger Amazon blogging products](https://dearblogger.org/amazon-blogging/) | 24 | public Amazon affiliate recommendation article |
| [GetReditus affiliate marketing tools](https://www.getreditus.com/blog/top-affiliate-marketing-tools/) | 12 | public SaaS/tools recommendation page |
| [Software Cronichle CI/CD tools](https://softwarecronichle.com/best-ci-cd-tools-for-software-teams/) | 2 | public tools recommendation page |

Selection notes:

- The operator first collected from `16` candidate public pages.
- The final sample used a manual content-quality filter to avoid noisy rows such as comments, pingbacks, generic nav/sidebar links, and non-recommendation links.
- Public collection used the repo's conservative `collect-web` path and respected robots.txt checks before fetching pages.
- The live checker used serial local execution with `10s` timeout, `1` retry, and `10` redirect hops.
- No public Telegram scraping, account access, proxy rotation, CAPTCHA solving, outreach, payment flow, or customer data was used.

## Manual QA Outcomes

All three automated candidate issues were manually checked against the source context and destination behavior in a browser.

| id | source context | target | observed issue | confidence |
| --- | --- | --- | --- | --- |
| `web-014` | TOBIQ 30L Travel Bag | `https://tobiqtravel.com/products/the-zion-tiny-tobiq` | destination rendered a visible TOBIQ `404 Page not found` | high |
| `web-064` | Reversible Corner Workcenter | `https://amzn.to/2XHyOry` | Amazon short link resolved to an Amazon `Page Not Found` destination during browser verification | medium |
| `web-082` | Sephora Ultra Moisturizing and Brightening Face-masks | `https://amzn.to/2JBpSjT` | Amazon short link resolved to an Amazon `Page Not Found` destination during browser verification | medium |

The Amazon confidence is `medium` rather than `high` because marketplace destinations can vary by bot controls, region, session, and availability state. They are still valid enough for a manual QA evidence set, but not safe enough for an automated browser-local broken-link claim.

## Metrics

| metric | value | gate | result |
| --- | ---: | ---: | --- |
| checked links | `100` | `>=100` | pass |
| confirmed meaningful issues | `3` | `>=5` | fail |
| confirmed issues per 100 links | `3.00` | `>=5.00` | fail |
| candidate false-positive rate | `0%` | `<=20%` | pass |
| blocked/ambiguous rate | `8%` | `<=20%` | pass |
| direct cost per 100 links | `$0` | `<$5` | pass |
| operator-recorded QA minutes per 100 links | `15` | `<60` | pass |
| value clarity score | `4/5` | `>=4/5` | pass |

Generated lane report verdict: `reshape`.

Important nuance: the lane report still includes the older dual-lane benchmark shape, so it marks the Telegram lane as incomplete. For this hub-first run, the relevant result is the web-affiliate row: `100` checked, `3` confirmed, `8%` blocked/ambiguous, `0%` candidate false positives.

## What This Proves

Evidence:

- Public affiliate/recommendation pages do contain buyer-visible monetized-link issues.
- The operator workflow can collect a rights-clean `100`-link web-affiliate sample without outreach or private data.
- A conservative live checker plus manual QA can find real broken/unavailable revenue-link destinations.
- Manual QA time can stay well below the `60` minutes per `100` links gate when candidates are sparse.
- The free hub drop-in analyzer remains the right P0 shape because it can help users build a local verification queue without expensive backend checks.

## What This Does Not Prove

Evidence gap:

- This batch did not prove that broad self-selected public pages reliably produce `>=5` confirmed meaningful issues per `100` links.
- It did not prove paid-report demand, conversion, retention, or willingness to pay.
- It did not prove AliExpress/Telegram demand.
- It did not prove that automated live status checks are safe enough for final broken-link verdicts.
- It did not prove that a SaaS dashboard, monitoring system, plugin, extension, or crawler fleet is warranted.

## Product Implications

Keep:

- Free local-first hub MVP.
- Deterministic local rule engine.
- No live fetch in the public P0 browser flow.
- `needs_verification` wording instead of automatic `broken` claims.
- Manual verification for any paid-report evidence.

Change or add:

- Add a collector/source-selection rule to exclude comment and pingback sections.
- Treat marketplace and Shopify-style destination volatility as verification-only, not auto-broken.
- Prefer owner-provided exports, stale evergreen money pages, or older Amazon roundup pages for the next paid-report proof.
- Keep pricing out of P0 until repeated proof batches or user uploads show stronger signal.

## Recommendation

Continue building the free KikuAI hub drop-in analyzer.

Do not launch the paid verified report yet. First run a second `100`-link proof batch with a stronger source hypothesis:

- older evergreen Amazon/marketplace roundup posts;
- owner-provided affiliate exports if available;
- pages with visible commercial intent and last-updated dates older than `18` months;
- no comments, nav/sidebar blocks, generic homepage links, or major-media/giant-site targets.

If the second batch still finds fewer than `5` confirmed meaningful issues per `100` links, park paid-report testing and focus only on the free local inventory/risk-report tool.
