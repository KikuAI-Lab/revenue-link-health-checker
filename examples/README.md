# Examples

Synthetic local files for trying the checker without customer data or live scraping.

Use these for demos, screenshots, README validation, and smoke tests. They are not evidence of real broken affiliate links.

## Sample Roundup

`sample-affiliate-roundup.txt` is a plain-text roundup excerpt with HTTP(S) links. It is useful for the dropzone offline deterministic mode and `extract-doc-links`.

```bash
python3 -m linkhealth extract-doc-links \
  --input-doc examples/sample-affiliate-roundup.txt \
  --output-csv .local/sample-roundup-links.csv
```

Then open the local dropzone:

```bash
python3 -m linkhealth dropzone
```

Drop the sample file and use **Offline deterministic diagnosis only** for a fast local report, or turn it off when you intentionally want outbound checks from your machine.
