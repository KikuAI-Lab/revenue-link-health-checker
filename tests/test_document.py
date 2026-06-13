from __future__ import annotations

import unittest

from linkhealth.document import extract_document_links, patch_document
from linkhealth.repair import RepairAction


class DocumentWorkflowTests(unittest.TestCase):
    def test_extracts_markdown_and_html_links_as_samples(self) -> None:
        text = (
            "# Best tools\n\n"
            "[Camera](https://shop.example/camera?tag=affiliate)\n\n"
            '<a href="https://tools.example/app">Recommended tool</a>\n'
            '<a href="/internal">Internal</a>\n'
            "[Mail](mailto:hello@example.com)\n"
        )

        samples = extract_document_links(text, filename="roundup.md")

        self.assertEqual(
            [sample.original_url for sample in samples],
            [
                "https://shop.example/camera?tag=affiliate",
                "https://tools.example/app",
            ],
        )
        self.assertEqual(samples[0].sample_id, "roundup-001")
        self.assertEqual(samples[0].source_reference, "roundup.md")
        self.assertEqual(samples[0].source_context, "Camera")
        self.assertEqual(samples[1].source_context, "Recommended tool")

    def test_patches_only_replace_with_url_actions(self) -> None:
        text = (
            "[Camera](https://shop.example/old) "
            "[Tool](https://tools.example/keep) "
            '<a href="https://blocked.example/item">Blocked</a>'
        )
        actions = [
            self._action(
                "web-001",
                action="replace_with_url",
                original_url="https://shop.example/old",
                replacement_url="https://shop.example/new",
            ),
            self._action(
                "web-002",
                action="keep",
                original_url="https://tools.example/keep",
            ),
            self._action(
                "web-003",
                action="manual_review",
                original_url="https://blocked.example/item",
            ),
        ]

        result = patch_document(text, actions)

        self.assertIn("https://shop.example/new", result.text)
        self.assertNotIn("https://shop.example/old", result.text)
        self.assertIn("https://tools.example/keep", result.text)
        self.assertIn("https://blocked.example/item", result.text)
        self.assertEqual(result.replacements_applied, 1)
        self.assertEqual(result.skipped_actions, 2)

    def _action(
        self,
        sample_id: str,
        *,
        action: str,
        original_url: str,
        replacement_url: str = "",
    ) -> RepairAction:
        return RepairAction(
            sample_id=sample_id,
            action=action,
            source_reference="roundup.md",
            source_context="Recommended product",
            original_url=original_url,
            final_url=original_url,
            replacement_url=replacement_url,
            editor_instruction="Test instruction",
            confidence="high",
            evidence="HTTP evidence",
            screenshot_or_evidence_path="",
        )


if __name__ == "__main__":
    unittest.main()
