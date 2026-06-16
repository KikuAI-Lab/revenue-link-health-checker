# Revenue Link Health Activation Sprint

This is the next validation lane after the free local MVP exists.

The goal is to learn whether qualified users bring real files, complete a report/export workflow, and ask for a next artifact. Do not treat page views, GitHub stars, or sample-only clicks as product proof.

## Current State

- Free local-first MVP exists.
- Standalone localhost dropzone exists.
- Offline deterministic diagnosis exists.
- Optional outbound checks run from the user's machine.
- Same-window replacement inputs and patched-file export exist.
- Paid report, monitoring, API, MCP, and bulk automation remain unproven.

## 7-Day Plan

| Day | Action | Evidence |
| --- | --- | --- |
| 1 | Verify the public page, README, sample file, dropzone, and event funnel. | Working sample run and fresh test output. |
| 2 | Publish one short demo video/GIF or a screenshot thread. | Public proof asset URL. |
| 3 | Share in 2-3 buyer-fit places where affiliate/recommendation link maintenance pain is already visible. | Source URLs and notes. |
| 4 | Prepare or run the stronger 100-link proof batch. | Benchmark kit or completed report. |
| 5 | Review usage events and source quality. | Counts for real file loads, completed previews, and downloads. |
| 6 | Make only small copy/demo fixes if users misunderstand the boundary or inputs. | Diff or no-op note. |
| 7 | Decide continue, hold, or park. | Short verdict with numbers. |

## Metrics To Review

- Qualified visits.
- `input_loaded`.
- `sample_loaded`.
- `preview_completed`.
- `sample_preview_completed`.
- `report_downloaded`.
- Patched-file downloads from the localhost dropzone, if manually observed.
- API/MCP or verified-report interest.
- Replies or comments that mention a real workflow.

Never collect raw URLs, file names, file contents, local paths, emails inside tool events, or private page data.

## Go / Hold / Park

Go if real buyer-fit users load their own files, complete previews, download reports, and ask for verified reports, API/MCP, folder mode, WordPress exports, or recurring checks.

Hold if traffic is qualified but sample-only, or if users understand the idea but need a clearer demo or a missing input parser.

Park paid-report work if qualified traffic does not produce real file loads or if the stronger proof batch again finds fewer than 5 manually confirmed meaningful issues per 100 checked links.
