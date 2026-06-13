from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.demo import run_demo


class DemoTests(unittest.TestCase):
    def test_offline_demo_writes_complete_artifact_set(self) -> None:
        output_dir = Path(tempfile.mkdtemp())

        result = run_demo(output_dir)

        self.assertEqual(result["verdict"], "select_p1b_web")
        self.assertEqual(result["links_checked"], 10)
        for name in (
            "samples.csv",
            "evidence.csv",
            "evidence.jsonl",
            "qa-decisions.csv",
            "reviewed-evidence.csv",
            "reviewed-evidence.jsonl",
            "repair-plan.csv",
            "repair-plan.json",
            "repair-plan.md",
            "report.md",
            "report.html",
            "report.json",
        ):
            self.assertTrue((output_dir / name).exists(), name)
        payload = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["verdict"], "select_p1b_web")

    def test_readme_direct_demo_command_runs_from_repo_root(self) -> None:
        output_dir = Path(tempfile.mkdtemp())
        repo_root = Path(__file__).resolve().parents[1]

        result = subprocess.run(
            [sys.executable, "scripts/demo.py", "--output-dir", str(output_dir)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((output_dir / "report.json").exists())


if __name__ == "__main__":
    unittest.main()
