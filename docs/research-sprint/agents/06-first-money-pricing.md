# First-Money Offer And Pricing Research

## Executive Verdict
The first offer that can plausibly get paid signal without building a full SaaS is a fixed-scope, self-serve, no-call **verified money-page report** at **$49**. Use a **$19-$29 paid export/report pack** as the bridge offer, keep the browser-local checker free, and hold monthly monitoring until you have proof that the report sells and repeats.

The market is already crowded with free broken-link tools and low-cost monitoring:
- Lasso is $19-$59/mo and includes broken link alerts in paid plans.
- PageRadar starts at €39/mo and sells geo-targeted affiliate-link monitoring.
- BetterLinks is $79-$279 for WordPress link management.
- Ahrefs has a free broken-link checker.
- Check My Links is a free Chrome extension with 90,000 users.
- AMZ Watcher offers a free broken-links report CTA and subscription plans with refund terms.

That means a **$9 manual audit is too cheap to look credible**. A human-verified artifact needs to sit above commodity automation, not below it.

## Offer packages table

| Package | Price | Buyer gets | What makes it credible | Call needed? |
|---|---:|---|---|---|
| Free browser-local checker | Free | Local CSV/HTML/Markdown parsing, risk flags, broken/redirect/out-of-stock heuristics, basic preview | Matches the product constraint: no upload, no live fetch, no AI, no payment | No |
| Paid export/report | $19-$29 | Polished PDF/HTML/CSV export, cleaned evidence, priority ranking, short exec summary, recommended fixes | Sits above free tools but below human service; good as an upsell after the local scan | No |
| Manual verified mini-audit | $49-$99 | Human-checked one-page money-page report or small batch verification report with confirmed issues, screenshots/evidence, and fix recommendations | This is the first offer that feels like expert work, not commodity checking | No |
| Monthly monitoring | After proof, likely $19-$39/mo starter, higher for volume | Ongoing checks and alerts for verified monetized/recommendation links only | Should only exist after the report proves demand and false positives are controlled | No, but only after proof |

## What stays free
- The browser-local checker itself.
- Local file import and parsing.
- Risk flags only, not human verification.
- Basic preview output.
- No upload workflow.
- No live fetch.
- No AI.
- No payment gate.

Free has to be useful enough to show signal, but not so complete that it replaces the paid artifact.

## What can be paid now
- A **paid export/report pack** at **$19-$29**.
- A **manual verified mini-audit** at **$49-$99**.
- A **one-page money-page report** is the best first-money artifact.
- A **small batch verification report** is the best higher-ticket version.

Best practical split:
- **$29**: automated, polished export.
- **$49**: one verified money page.
- **$99**: small batch, verified, with evidence and prioritization.

## What must wait
- Monthly monitoring as the core product.
- Dashboard-first SaaS.
- Any API.
- Any bulk automation beyond the local checker.
- Any subscription until you know the paid report converts.
- Any promise of continuous alerts before you have proof that users will pay for a one-time verified result.

## Payment/no-call flow
- User runs the free local checker.
- User sees a clear “unlock verified report” CTA.
- User pays for a fixed-scope report.
- User submits the page set or file for manual verification.
- You deliver the report asynchronously.

This can be bought without a call because the scope is narrow and the output is concrete. The call would only add friction.

## Refund/risk policy
- If no confirmed monetized-link issue is found, do not charge for the verified audit.
- If the report contains a false positive that materially changes the result, refund or rework it.
- Exclude blocked, CAPTCHA, login-gated, geo-dependent, and rate-limited cases from “confirmed broken” claims.
- Promise a revision once, not open-ended support.
- Do not make ROI or revenue-loss guarantees.

## Kill criteria
- Kill the offer if you cannot find at least **5 confirmed issues per 100 links** in the chosen lane.
- Kill it if false positives or blocked/ambiguous cases exceed **20%**.
- Kill it if manual QA takes more than **60 minutes per 100 links**.
- Kill it if the only thing prospects want is generic broken-link checking.
- Kill it if you cannot close a no-call paid report after a small targeted test set.
- Kill it if the offer needs a dashboard or recurring monitoring to justify the first sale.

## Sources and assumptions
Current official pricing/offer pages reviewed on 2026-06-11:
- [Lasso pricing](https://getlasso.co/pricing/)
- [BetterLinks pricing](https://betterlinks.io/pricing/)
- [PageRadar affiliate link checker](https://pageradar.io/features/affiliate-link-checker)
- [Ahrefs broken link checker](https://ahrefs.com/broken-link-checker)
- [Check My Links Chrome Web Store](https://chromewebstore.google.com/detail/check-my-links/aajoalonednamcpodaeocebfgldhcpbe?hl=en-US)
- [AMZ Watcher pricing](https://amzwatcher.com/pricing/)

Local project context used:
- [README.md](../../README.md)
- [affiliate-revenue-link-health-mvp-prd.md](../../docs/affiliate-revenue-link-health-mvp-prd.md)

Assumptions:
- Currency comparisons are directional; I did not convert EUR to USD with live FX.
- The PRD’s 2026-06-01 competitor snapshot is still useful for context, especially for JS-heavy pages and for the Brokenly/AffilGuard references that were not re-opened cleanly today.
- The best first-money artifact is a **fixed-scope verified report**, not a monitoring subscription.