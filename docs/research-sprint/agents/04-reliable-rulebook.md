# Reliable Rulebook Research
## Executive Verdict
A safe deterministic V1 exists, but it is mostly a local classifier plus a narrow live-verification queue. The rules that can auto-resolve locally are the ones that are structurally invalid or unsupported: malformed URLs, unsupported schemes, and exact normalized duplicates. Everything that depends on marketplace behavior, affiliate attribution, redirect chains, region/store availability, or final destination state should stay in a `needs_verification` lane unless you have live confirmation.

## Rule table

| Rule name | Detection method | Confidence | False positive risk | User-facing wording | Recommended action | Free/local vs live verification | Test fixture examples |
|---|---|---:|---:|---|---|---|---|
| Malformed URL | Parse fails, missing host on absolute URL, bad scheme syntax, illegal characters, or empty URL. | High | Low | `Malformed URL` | Reject before QA; do not send as a broken-link claim. | Free/local | `ht!tp://example.com`, `https://`, `://bad` |
| Non-http URL | Scheme is not `http` or `https` (`mailto`, `tel`, `javascript`, `data`, `ftp`, `intent`, `sms`, etc.). | High | Low | `Unsupported link scheme` | Exclude from broken-link scoring or route to a separate deep-link queue. | Free/local | `mailto:ops@example.com`, `tel:+15551234567`, `javascript:void(0)` |
| Duplicate normalized destination | Normalize scheme/host casing, empty path, and fragment removal; compare full destination including query unless a platform-specific rule says otherwise. | High | Medium | `Duplicate destination` | Deduplicate the list; keep one canonical row and preserve the original rows for traceability. | Free/local | `https://example.com/page#one` vs `https://example.com/page#two` |
| Affiliate/referral parameters | Look for referral-style query keys such as `ref`, `ref_id`, `aff`, `aff_id`, `affiliate`, `partner`, `subid`, `clickid`, `irclickid`, `sid`, etc. | Medium | Medium | `Referral/affiliate tracking detected` | Inventory only; preserve the original URL and do not strip parameters in canonicalization. | Free/local; live only if the final destination itself must be verified | `https://merchant.example/p?ref=publisher123`, `...?aff_id=42` |
| Tracking parameters | Detect campaign keys such as `utm_*`, `gclid`, `fbclid`, `msclkid`, `mc_cid`, `mc_eid`, `igshid`, `spm`, `cmpid`. | High | Medium-low | `Campaign tracking detected` | Inventory only; never call it broken just because tracking is present. | Free/local | `https://example.com/?utm_source=newsletter&utm_campaign=spring`, `...?gclid=abc` |
| Marketplace/shortener/network hosts | Match against a curated host-family list for marketplaces, shorteners, and link networks; do not infer breakage from host alone. | Medium | Medium-high | `Marketplace or shortener host detected` | Classify as high-risk and defer to platform-specific rules; do not auto-label broken. | Free/local classification; live verification only for final destination state | `https://bit.ly/abc`, `https://linktr.ee/name`, `https://goo.gl/vLUcaJ` |
| Missing anchor/source context | Source row has empty `source_context`/anchor text, or extraction yielded only nav/footer/social context. | High | Low | `Missing source context` | Mark the row as low-evidence; require source URL, anchor text, or screenshot before owner-facing output. | Free/local | CSV row with blank `source_context`, HTML link from a footer icon only |
| Suspicious redirector domains | URL itself is a redirector or contains redirect-style path/query hints like `/go`, `/out`, `/redirect`, `url=`, `target=`, `u=`. | Medium | Medium-high | `Redirector needs verification` | Route to manual browser confirmation or live verification before any user-facing claim. | Local detection; live verification required for the final target | `https://publisher.example/go?url=https%3A%2F%2Fmerchant.example%2Fitem` |
| Mixed region marketplace links | Detect country/locale signals in storefront URLs and compare them to declared audience/market context. | Medium-low | High | `Possible wrong-region store link` | Do not call it broken; verify against the target region before surfacing. | Local detection of mismatch markers; live verification needed for region/state | `https://apps.apple.com/us/app/...` with UK audience, `...&gl=US` vs a non-US target |
| Amazon tag patterns | Match Amazon domains plus `tag=` and related special-link patterns; Amazon’s current agreement says special links must use tagged formats. | High for classification | Low-medium | `Amazon Associates-style link detected` | Preserve `tag`; do not normalize it away. Do not claim breakage unless the destination itself is confirmed bad. | Free/local classification; live only if the destination state matters | `https://www.amazon.com/dp/B0... ?tag=owner-20` |
| AliExpress short-link patterns | Match known AliExpress short-link hosts/families such as `s.click.aliexpress.com` and `a.aliexpress.com` plus short-token paths. | Medium | Medium-high | `AliExpress short link detected` | Keep as a short-link/redirector classification; live-check only if product state or destination correctness matters. | Free/local classification; live verification for availability/destination correctness | `https://s.click.aliexpress.com/e/_mP0abc1`, `https://a.aliexpress.com/_m0xyz` |
| SaaS/app-store link patterns | Match software marketplace/store families such as `apps.apple.com/.../id...`, `play.google.com/store/apps/details?id=...`, and similar store URLs. | Medium-high | Medium | `App-store or software marketplace link detected` | Separate these from ordinary web links and use platform-specific live checks for install, availability, or region gating. | Free/local classification; live verification for availability/geo gating | `https://apps.apple.com/us/app/garageband/id408709785`, `https://play.google.com/store/apps/details?hl=en&id=com.google.android.apps.maps` |

## Rules to avoid
- Do not treat `403`, `429`, login walls, CAPTCHA pages, geo blocks, or robots-denied fetches as broken links.
- Do not strip `utm`, `tag`, or referral parameters and then use the stripped URL as proof of duplication or failure.
- Do not call a shortener or redirector broken just because the final destination is hidden.
- Do not infer AliExpress product unavailability, App Store unavailability, or region mismatch from URL shape alone.
- Do not use AI to finalize broken/unavailable verdicts.
- Do not collapse distinct regional store URLs into one duplicate bucket unless you explicitly opt into region-aware canonicalization.
- Do not turn missing source context into a broken-link claim.

## Recommended V1 rule changes
- Split output into three buckets: `invalid`, `needs_verification`, and `inventory_only`.
- Keep canonicalization conservative: lowercase scheme/host, remove fragments, preserve query strings, and never strip affiliate/tracking parameters by default.
- Make host-family lists data-driven and test-backed, not hardcoded logic buried in the checker.
- Require source context for any owner-facing preview or alert involving redirectors, shorteners, or marketplace links.
- Keep region/store rules separate from broken-link rules; they are verification rules, not auto-fail rules.
- Add explicit fixture coverage for Amazon tags, AliExpress short links, Google Play URLs, Apple App Store URLs, UTM parameters, and generic redirectors.

## Sources and assumptions
Local scope and current implementation context:
- [README.md](../../README.md)
- [Affiliate Revenue-Link Health MVP PRD](../../docs/affiliate-revenue-link-health-mvp-prd.md)
- [QA Broken Links Hub Drop-In V0 Design](../../docs/superpowers/specs/2026-06-11-qa-broken-links-hub-drop-in-v0-design.md)
- [linkhealth/checker.py](../../linkhealth/checker.py)
- [tests/test_checker.py](../../tests/test_checker.py)
- [tests/test_web.py](../../tests/test_web.py)

Web sources used for current claims:
- [Amazon Associates Program Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement)
- [Google Analytics URL builders](https://support.google.com/analytics/answer/1033867?hl=en)
- [GarageBand on the App Store](https://apps.apple.com/us/app/garageband/id408709785)
- [Google Maps on Google Play](https://play.google.com/store/apps/details?hl=en&id=com.google.android.apps.maps)

Assumptions:
- Amazon’s current agreement confirms that Special Links must use tagged link formats, but it does not publish a full parameter schema in the text I fetched. I am inferring `tag=` as the practical local detector because that matches current public Amazon affiliate URL shape.
- I did not find current official AliExpress documentation for the short-link family in this pass. The AliExpress rule should therefore stay heuristic and configurable, not a hard compliance claim.
- The Google Play and App Store rules are based on stable URL family patterns and should stay verification-only for availability, install gating, and region behavior.