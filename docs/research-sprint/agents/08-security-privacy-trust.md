# Security, Privacy, And Trust Research

## Executive Verdict
The safest sellable positioning is `local-first link-health analysis`, not `browser-local`, unless the shipping UI truly runs the scan in the browser. The checked-in implementation is a local Python workflow that fetches target URLs directly and writes local CSV/JSONL/HTML/MD artifacts, so the trust story should match that reality rather than outgrow it.

You can sell this without SOC2 or enterprise review if you keep the claims narrow:
- no account for the free workflow
- no file upload for the free workflow
- no backend analysis for the free workflow
- public pages only, with robots.txt respected
- human-reviewed confirmation before an issue is called
- explicit disclosure of limits and ambiguity

Local code proof:
- [README.md](../../README.md#L3) / [README.md](../../README.md#L8)
- [linkhealth/checker.py](../../linkhealth/checker.py#L75)
- [linkhealth/web.py](../../linkhealth/web.py#L123)
- [linkhealth/workflow.py](../../linkhealth/workflow.py#L54)
- [linkhealth/report.py](../../linkhealth/report.py#L54)

## Safe trust claims
These are safe if they remain true in the shipped product:

- `Runs locally on your machine` or `local-first`, but not `browser-local` unless the browser actually executes the workflow.
- `No account required for the free report`.
- `No file upload for the free workflow`.
- `No backend analysis for the free workflow`.
- `Public pages only`.
- `robots.txt is checked before public-page collection`.
- `We do not scrape public Telegram`.
- `We do not use proxy rotation, CAPTCHA solving, identity spoofing, or rate-limit evasion`.
- `We preserve original URLs, redirect chains, timestamps, status evidence, and ambiguous outcomes`.
- `Blocked, CAPTCHA-like, login-gated, geo-dependent, and rate-limited results stay ambiguous instead of being guessed`.
- `Human QA is required before a candidate issue is confirmed`.
- `The workflow is deterministic and inspectable`.
- `No API keys`, `no AliExpress API dependency`, `no AI dependency` if those remain true.
- `We disclose affiliate/material connections clearly and near the endorsement if our own site uses affiliate links`.

FTC guidance to align with:
- material connections must be obvious
- disclosures should be hard to miss and placed with the endorsement
- simple words like `ad` or `sponsored` are better than vague shorthand
- avoid burying disclosures in footers or `about` pages

Source:
- FTC Disclosures 101: [FTC Disclosures 101 for Social Media Influencers](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers)

## Dangerous claims
These are risky or false unless you have the evidence and controls to support them:

- `SOC2 compliant`
- `enterprise-grade secure`
- `privacy certified`
- `GDPR compliant`
- `CCPA compliant`
- `legally compliant`
- `compliance approved`
- `legal advice`
- `guaranteed revenue loss estimates`
- `100% accurate broken-link detection`
- `zero false positives`
- `nothing ever leaves your device` if you have any analytics, CDN, telemetry, email delivery, payment processing, or hosted paid-report flow
- `we monitor public Telegram channels` or `we can scrape private channels`
- `we bypass CAPTCHAs / login / geo restrictions`
- `we can tell you exactly how much money a broken link costs`

The biggest overreach to avoid is turning a technical evidence tool into a compliance or legal certainty product. The FTC’s deception standard is about avoiding misleading omissions and making sure disclosures are clear and conspicuous; it is not a shield for broad guarantees you cannot prove.

## Privacy FAQ bullets
Use short, plain answers like these on the page:

- `What do you collect?` We collect only what you submit for a check and the local report outputs; the free workflow runs locally.
- `Do you upload my files?` Not for the free local workflow.
- `Do you store my links on a server?` Not for the free local workflow.
- `Do you use cookies or trackers?` Avoid third-party ad trackers, session replay, and heatmaps; if you use any analytics, keep them first-party and minimal.
- `Do you sell data?` No.
- `How long do you keep data?` Local files stay under your control; any future hosted workflow should state retention and deletion windows explicitly.
- `Can I delete my data?` If we ever store anything server-side, deletion should be available and documented.
- `Is this legal advice?` No. It is operational risk guidance, not legal advice or a compliance certification.
- `Do you respect source permissions?` Yes for public pages with robots.txt allowed sources; no public Telegram scraping, no bypassing access controls.

FTC and California privacy guidance to keep in mind:
- affiliate/material relationships should be disclosed clearly and near the claim
- privacy policies should explain what personal information is collected, why, how it is used, who gets it, what choices users have, what security measures are used, and who to contact
- if you collect California residents’ personal information, CalOPPA/CCPA-related disclosure duties may apply depending on your operation

Source:
- California DOJ privacy-policy guidance: [How to Read a Privacy Policy](https://oag.ca.gov/privacy/facts/online-privacy/privacy-policy)

## Technical trust checklist
What you can show publicly to build trust without claiming SOC2:

- A simple architecture diagram: user input -> local check -> local evidence files -> local report.
- A local demo run that produces `samples.csv`, `evidence.csv/jsonl`, `reviewed-evidence.csv/jsonl`, and `report.md/html/json`.
- A code excerpt or repo link showing the local-only flow and the absence of a backend API.
- A network tab or terminal capture showing only direct requests to target URLs and no app backend calls.
- A visible note that the checker respects `robots.txt` and treats blocked or ambiguous states as ambiguous.
- A visible note that candidate issues require human QA before they are confirmed.
- A visible note that the free workflow is local and that any future paid flow will disclose uploads, retention, and processing boundaries.
- A visible privacy policy and terms page, even if the product is small.

Good proof artifacts already in the repo:
- local demo output bundle in the README
- explicit consent tracking for `telegram_aliexpress` rows
- explicit ambiguity handling in the checker
- public-page-only collection logic in the web collector
- local CSV/JSONL report generation

## Analytics/logging limits
Avoid these by default:

- third-party ad trackers
- session replay
- heatmaps
- fingerprinting
- cross-site identifiers
- pixels from ad platforms
- full URL logging to shared analytics
- logging query strings or redirect chains in remote analytics
- logging page bodies, screenshots, or HTML into server-side logs
- storing IP addresses longer than needed
- storing user-agent strings unless you truly need them for security or abuse handling
- retaining full source pages or source_context text in analytics systems
- logging paid customer inputs into vendor tools that are not needed for fulfillment

If you need metrics, keep them coarse:
- run count
- report generation count
- lane selected
- error category counts
- approximate latency
- aggregate QA time

Do not send raw link data to analytics just to get a dashboard.

## Minimum paid-report trust requirements
Before selling paid reports, you need at least this:

- a public privacy policy
- a public terms page
- a short scope statement saying exactly what the paid report does and does not do
- a clear data-flow statement: what is submitted, where it is processed, what is retained, and for how long
- a clear statement whether the paid report is still local or becomes hosted
- a payment processor that handles card data directly
- no raw card storage
- a deletion and retention policy
- a support/contact path
- a basic incident-response contact
- a clear refund/cancellation policy
- a clear disclosure if any paid workflow uses analytics or third-party subprocessors
- a simple security baseline: HTTPS, least privilege, secrets management, and dependency hygiene

If the paid workflow moves off-device, stop saying `no upload` and replace it with precise language about what is uploaded, where it goes, and how long it is kept.

## Abuse cases
Most likely misuse modes to design against:

- private or login-gated scraping
- public Telegram scraping for dataset building
- CAPTCHA, geo, or rate-limit bypass attempts
- using the report to make unsupported claims of revenue damage
- using the tool to harass or defame a site owner
- uploading sensitive URLs, credentials, or regulated-content pages by mistake
- claiming the output is a legal or compliance certification
- treating ambiguous results as confirmed failures
- using analytics to rebuild user link datasets without consent

Guardrails:
- keep the public-sources boundary hard
- keep ambiguity visible
- require human QA before confirmation
- do not add bypass features
- do not log more than you need
- do not market the output as legal advice

## Sources and assumptions
Primary sources used:
- FTC, `Disclosures 101 for Social Media Influencers`: https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers
- California DOJ, `How to Read a Privacy Policy`: https://oag.ca.gov/privacy/facts/online-privacy/privacy-policy

Local repo evidence used:
- [README.md](../../README.md)
- [docs/affiliate-revenue-link-health-mvp-prd.md](../../docs/affiliate-revenue-link-health-mvp-prd.md)
- [linkhealth/checker.py](../../linkhealth/checker.py)
- [linkhealth/web.py](../../linkhealth/web.py)
- [linkhealth/io.py](../../linkhealth/io.py)
- [linkhealth/workflow.py](../../linkhealth/workflow.py)
- [linkhealth/report.py](../../linkhealth/report.py)

Assumptions:
- the current product remains local-first and does not add a hosted analysis backend before paid reports
- no third-party analytics are required
- no account system is required for the free workflow
- no legal or compliance certification is being promised
- paid reports, if added, will be explicitly separated from the free local flow with their own privacy and retention language