from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from linkhealth.io import load_samples
from linkhealth.models import InputValidationError


class LoadSamplesTests(unittest.TestCase):
    def test_loads_csv_and_preserves_source_fields(self) -> None:
        path = self._write(
            "samples.csv",
            "sample_id,lane,consent_basis,source_reference,source_context,original_url\n"
            'web-001,web_affiliate,public_page,https://example.com/resources,"Camera row",'
            "https://merchant.example/product?tag=owner-20\n",
        )

        samples = load_samples(path)

        self.assertEqual(len(samples), 1)
        self.assertEqual(samples[0].sample_id, "web-001")
        self.assertEqual(samples[0].source_reference, "https://example.com/resources")
        self.assertEqual(samples[0].original_url, "https://merchant.example/product?tag=owner-20")

    def test_loads_jsonl(self) -> None:
        path = self._write(
            "samples.jsonl",
            json.dumps(
                {
                    "sample_id": "tg-001",
                    "lane": "telegram_aliexpress",
                    "consent_basis": "admin_export_2026-06-01",
                    "source_reference": "approved-channel-a",
                    "source_context": "post 481",
                    "original_url": "https://s.click.aliexpress.com/example",
                }
            )
            + "\n",
        )

        samples = load_samples(path)

        self.assertEqual(samples[0].lane, "telegram_aliexpress")

    def test_rejects_telegram_row_without_consent_basis(self) -> None:
        path = self._write(
            "samples.csv",
            "sample_id,lane,consent_basis,source_reference,source_context,original_url\n"
            "tg-001,telegram_aliexpress,,approved-channel-a,post 481,https://example.com/item\n",
        )

        with self.assertRaisesRegex(InputValidationError, "consent_basis"):
            load_samples(path)

    def test_rejects_missing_required_field(self) -> None:
        path = self._write(
            "samples.csv",
            "sample_id,lane,consent_basis,source_reference,source_context\n"
            "web-001,web_affiliate,public_page,https://example.com/resources,Camera row\n",
        )

        with self.assertRaisesRegex(InputValidationError, "original_url"):
            load_samples(path)

    def test_rejects_non_http_url(self) -> None:
        path = self._write(
            "samples.csv",
            "sample_id,lane,consent_basis,source_reference,source_context,original_url\n"
            "web-001,web_affiliate,public_page,https://example.com/resources,Camera row,mailto:test@example.com\n",
        )

        with self.assertRaisesRegex(InputValidationError, "http"):
            load_samples(path)

    def _write(self, name: str, body: str) -> Path:
        directory = Path(tempfile.mkdtemp())
        path = directory / name
        path.write_text(body, encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
