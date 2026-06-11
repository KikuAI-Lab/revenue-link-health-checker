# Competitor And Substitute Research

## Executive Verdict
The market already has strong coverage for generic broken-link checking, affiliate-link monitoring, WordPress link management, and broad SEO audits. What it does **not** clearly have is a fast, browser-local, no-upload, no-AI pre-flight review for monetized/recommendation content that flags **risk signals in CSV/HTML/Markdown before the user pays for heavier tooling**.

That means your real wedge is not “better broken-link checker.” It is “private, proof-before-pay link-risk triage for small publishers.”

## Competitor Map
| Segment | Who | What they solve now | Why it matters |
|---|---|---|---|
| Live affiliate monitoring | [AffilGuard](https://affilguard.io/), [PageRadar](https://pageradar.io/features/affiliate-link-checker), [AMZ Watcher](https://amzwatcher.com/pricing/) | Daily/hourly checks, broken-link alerts, redirect-chain checks, stripped-tracking detection, geo-targeting, Amazon focus | These already cover the “keep my affiliate links alive” job. |
| Generic broken-link checking | [Ahrefs Broken Link Checker](https://ahrefs.com/broken-link-checker), [Check My Links](https://chromewebstore.google.com/detail/check-my-links/aajoalonednamcpodaeocebfgldhcpbe?hl=en-US), [lychee](https://github.com/lycheeverse/lychee) | Free or local checking for broken URLs in sites, Markdown, HTML, and browser pages | This is commoditized. Users already have cheap/free ways to check links. |
| WordPress affiliate plugins | [Lasso](https://getlasso.co/pricing/), [ThirstyAffiliates](https://thirstyaffiliates.com/pricing), [BetterLinks](https://betterlinks.io/pricing/) | Link management, redirects, disclosures, broken-link alerts/checkers inside WP | These own the “site owner installs a plugin” path. |
| Broad SEO suites | [Semrush Site Audit](https://www.semrush.com/siteaudit/), [Ahrefs Broken Link Checker](https://ahrefs.com/broken-link-checker) | Site-wide crawling, technical SEO audits, reporting, scheduling | They are heavier than a publisher usually wants for a simple revenue-link audit. |

### Quick answers to your questions
- **Who already solves live broken links?** [AffilGuard](https://affilguard.io/), [PageRadar](https://pageradar.io/features/affiliate-link-checker), [AMZ Watcher](https://amzwatcher.com/pricing/), [Ahrefs Broken Link Checker](https://ahrefs.com/broken-link-checker), [Semrush Site Audit](https://www.semrush.com/siteaudit/), [Check My Links](https://chromewebstore.google.com/detail/check-my-links/aajoalonednamcpodaeocebfgldhcpbe?hl=en-US), and [lychee](https://github.com/lycheeverse/lychee).
- **Who solves affiliate/revenue-link context specifically?** [AffilGuard](https://affilguard.io/), [PageRadar](https://pageradar.io/features/affiliate-link-checker), [AMZ Watcher](https://amzwatcher.com/pricing/), [Lasso](https://getlasso.co/pricing/), [ThirstyAffiliates](https://thirstyaffiliates.com/pricing), and [BetterLinks](https://betterlinks.io/pricing/).
- **Who offers free checking?** [AffilGuard](https://affilguard.io/) (`20` links free), [PageRadar](https://pageradar.io/features/affiliate-link-checker) (free live test, no signup), [AMZ Watcher](https://amzwatcher.com/pricing/) (free broken-links report), [Lasso](https://getlasso.co/pricing/) (`1` property free), [Ahrefs Broken Link Checker](https://ahrefs.com/broken-link-checker) (free tool), [Check My Links](https://chromewebstore.google.com/detail/check-my-links/aajoalonednamcpodaeocebfgldhcpbe?hl=en-US) (free extension), and [lychee](https://github.com/lycheeverse/lychee) (open source).
- **Who offers proof-before-pay or browser-local privacy?** Proof-before-pay is strongest in [AffilGuard](https://affilguard.io/), [PageRadar](https://pageradar.io/features/affiliate-link-checker), and [AMZ Watcher](https://amzwatcher.com/pricing/) because they all have free entry points. Browser-local / local-only is strongest in [Check My Links](https://chromewebstore.google.com/detail/check-my-links/aajoalonednamcpodaeocebfgldhcpbe?hl=en-US), [Ahrefs Broken Link Checker](https://ahrefs.com/broken-link-checker) via browser toolbar, and [lychee](https://github.com/lycheeverse/lychee) as a local CLI.
- **Where are existing tools too heavy, too expensive, or wrong for small publishers?** [Semrush Site Audit](https://www.semrush.com/siteaudit/) is a broad SEO audit product, [PageRadar](https://pageradar.io/features/affiliate-link-checker) starts at `€39/mo`, WP plugins like [BetterLinks](https://betterlinks.io/pricing/) and [ThirstyAffiliates](https://thirstyaffiliates.com/pricing) require installation and ongoing plugin ownership, and affiliate monitors like [AffilGuard](https://affilguard.io/) still assume a monitoring workflow rather than a one-shot evidence pass.

## Substitute Map
- **Manual VA checks / spreadsheet audits:** still a real substitute. [PageRadar](https://pageradar.io/features/affiliate-link-checker) explicitly compares itself to manual checking and says the time cost is material; [AffilGuard](https://affilguard.io/) says checking `50+` links weekly can take hours.
- **Affiliate network dashboards:** useful for clicks, conversions, and payouts, but they solve the downstream reporting problem rather than the on-page content-health problem. That is an inference from the category, not a current dashboard page I verified in this pass.
- **SEO crawlers:** [Semrush Site Audit](https://www.semrush.com/siteaudit/) and [Ahrefs Broken Link Checker](https://ahrefs.com/broken-link-checker) solve the broader “website health” problem, not the “is this monetized recommendation page trustworthy enough to ship” problem.
- **Generic website link tools:** [Check My Links](https://chromewebstore.google.com/detail/check-my-links/aajoalonednamcpodaeocebfgldhcpbe?hl=en-US) and [lychee](https://github.com/lycheeverse/lychee) are excellent at raw link detection, but they are not revenue-context products.

## Our possible wedge
- Browser-local, no-upload, no-AI, no-payment.
- Accepts `CSV`, `HTML`, and `Markdown`.
- Flags **risk signals** on monetized/recommendation links instead of pretending to be a full monitoring system.
- Gives small publishers a fast “proof before you buy” pass on content they already have.
- Fits users who want privacy and low friction more than a dashboard.

## Claims we cannot make
- We cannot claim to provide definitive live destination verification, because the MVP has **no live status checks**.
- We cannot claim to replace ongoing affiliate monitors or geo-targeted checkers.
- We cannot claim to be a full SEO audit suite or WordPress link manager.
- We cannot claim perfect accuracy or complete coverage across every affiliate network.
- We cannot claim to quantify exact lost revenue from every flagged issue.

## Pricing Anchors
- Free: [Check My Links](https://chromewebstore.google.com/detail/check-my-links/aajoalonednamcpodaeocebfgldhcpbe?hl=en-US), [lychee](https://github.com/lycheeverse/lychee), [Ahrefs Broken Link Checker](https://ahrefs.com/broken-link-checker), [AMZ Watcher](https://amzwatcher.com/pricing/) free report, [Lasso](https://getlasso.co/pricing/) free tier.
- Low-cost monitoring: [AffilGuard](https://affilguard.io/) at `20` links free, then `$19/month`.
- Mid-range affiliate monitoring: [PageRadar](https://pageradar.io/features/affiliate-link-checker) from `€39/mo`.
- WordPress plugin pricing: [ThirstyAffiliates](https://thirstyaffiliates.com/pricing) starts at about `US$99.60/year` on the current page; [BetterLinks](https://betterlinks.io/pricing/) shows `US$79-$279` promotional pricing.
- Broader suite behavior: [Semrush Site Audit](https://www.semrush.com/siteaudit/) and [Ahrefs Broken Link Checker](https://ahrefs.com/broken-link-checker) are part of larger SEO platforms, so they compete on broader operations rather than narrow publisher-specific triage.

## Strongest reason to use us
You want a private, browser-local way to inspect monetized/recommendation content and get a fast, credible risk triage **before** you spend time or money on monitoring, plugins, or an SEO suite.

## Strongest reason not to use us
If you need continuous monitoring, geo-targeted checks, redirect-chain surveillance, or live broken-link verification, the existing tools already do that better and more completely.

## Sources
- [AffilGuard](https://affilguard.io/)
- [PageRadar affiliate link checker](https://pageradar.io/features/affiliate-link-checker)
- [AMZ Watcher pricing](https://amzwatcher.com/pricing/)
- [Lasso pricing](https://getlasso.co/pricing/)
- [ThirstyAffiliates pricing](https://thirstyaffiliates.com/pricing)
- [BetterLinks pricing](https://betterlinks.io/pricing/)
- [Ahrefs Broken Link Checker](https://ahrefs.com/broken-link-checker)
- [Semrush Site Audit](https://www.semrush.com/siteaudit/)
- [Check My Links Chrome Web Store](https://chromewebstore.google.com/detail/check-my-links/aajoalonednamcpodaeocebfgldhcpbe?hl=en-US)
- [lychee GitHub](https://github.com/lycheeverse/lychee)
