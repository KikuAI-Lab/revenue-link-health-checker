# Stronger Proof Batch 2

Run this only with rights-clean public pages or owner-provided exports. This is not a public scraping lane.

## Hypothesis

Older evergreen affiliate and marketplace roundup pages have a higher density of meaningful link issues than broad self-selected public recommendation pages.

## Source Selection

Prefer:

- older evergreen Amazon or marketplace roundup posts;
- niche review pages with visible commercial recommendations;
- SaaS/tools directories with commercial outbound links;
- owner-provided exports;
- pages with visible update dates older than 12 months.

Exclude:

- comments, pingbacks, nav/sidebar rows, homepages, and generic major-media pages;
- private, authenticated, paywalled, or login-gated pages;
- public Telegram scraping;
- CAPTCHA solving, proxy rotation, browser-identity spoofing, and rate-limit evasion.

## Run Kit

Create the local templates:

```bash
python3 -m linkhealth benchmark-init --run-dir .local/proof-batch-2
```

Populate:

- `.local/proof-batch-2/prospect-list.csv`;
- `.local/proof-batch-2/samples.csv`;
- `.local/proof-batch-2/metrics-log.csv`.

Then run:

```bash
python3 -m linkhealth check \
  --input .local/proof-batch-2/samples.csv \
  --output-csv .local/proof-batch-2/evidence.csv \
  --output-jsonl .local/proof-batch-2/evidence.jsonl

python3 -m linkhealth apply-qa \
  --evidence .local/proof-batch-2/evidence.csv \
  --decisions .local/proof-batch-2/qa-decisions.csv \
  --output-csv .local/proof-batch-2/reviewed-evidence.csv \
  --output-jsonl .local/proof-batch-2/reviewed-evidence.jsonl

python3 -m linkhealth report \
  --evidence .local/proof-batch-2/reviewed-evidence.csv \
  --output-json .local/proof-batch-2/report.json \
  --output-markdown .local/proof-batch-2/report.md \
  --output-html .local/proof-batch-2/report.html
```

## Gate

Continue the paid verified-report wedge only if the batch reaches:

- at least 100 checked rights-clean links;
- at least 5 manually confirmed meaningful issues per 100 checked links;
- false positives after manual QA at or below 20%;
- blocked/ambiguous outcomes at or below 20%;
- less than 60 manual QA minutes per 100 links;
- no complaints, no access-control bypass, no private data.

If the batch misses the issue-density gate again, keep the tool as a free local utility and do not build monitoring, SaaS, outreach, or paid reports.
