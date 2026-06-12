# Validation Notes

## First Web-Affiliate Proof Batch

Date: 2026-06-11

Status: executed, manually reviewed

Decision: reshape source selection before making any paid-report promise.

## Summary

A first operator-selected public web-affiliate batch checked `100` rights-clean public affiliate/recommendation links from `6` public pages.

Results:

- checked links: `100`;
- automated candidate issues: `3`;
- manually confirmed meaningful issues: `3`;
- confirmed issues per `100` links: `3`;
- initial gate: `>=5` confirmed meaningful issues per `100` links;
- blocked or ambiguous results: `8`;
- candidate false positives after manual QA: `0`;
- operator-recorded manual QA time: `15` minutes;
- direct infrastructure/API cost: `$0`.

This supports the value of a conservative local-first link-health workflow, but it does not yet prove a repeatable paid verified-report offer from broad self-selected public pages.

## Public Source Mix

The batch used public recommendation, roundup, and tools-directory pages. Collection avoided private pages, account-gated sources, public Telegram scraping, proxy rotation, CAPTCHA solving, payment flows, outreach, and customer data.

The final sample was manually filtered to remove noisy rows such as comments, pingbacks, navigation/sidebar links, and generic non-recommendation links.

## Confirmed Issue Types

Manual QA confirmed:

- one product destination rendering a visible `404 Page not found`;
- two Amazon short-link destinations resolving to Amazon `Page Not Found` states during browser verification.

Marketplace and short-link outcomes can vary by region, session, bot controls, and availability state. They should stay verification-only and should not be treated as safe automated broken-link claims.

## Implications

Keep:

- local-first import/check/report flow;
- deterministic rule engine;
- manual QA before confirmed issue claims;
- `candidate_issue` and `blocked_or_ambiguous` wording for raw automated checks.

Do not claim yet:

- repeatable paid-report demand;
- reliable `>=5` confirmed issues per `100` broad public links;
- AliExpress/Telegram demand;
- SaaS, dashboard, extension, plugin, monitoring, or crawler-fleet readiness.

## Next Validation Step

Run a second `100`-link proof batch with stronger source selection:

- older evergreen Amazon/marketplace roundup posts;
- owner-provided affiliate exports when available;
- pages with visible commercial intent and older update dates;
- no comments, nav/sidebar blocks, generic homepage links, or broad major-media targets.
