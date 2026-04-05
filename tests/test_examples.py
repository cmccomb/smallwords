from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = [
    ROOT / "examples" / "customer_support_chat.py",
    ROOT / "examples" / "neighbor_intro_chat.py",
    ROOT / "examples" / "bridge_explain.py",
]


def test_examples_run() -> None:
    for example in EXAMPLES:
        completed = subprocess.run(
            [sys.executable, str(example)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        assert "=== Prompt ===" in completed.stdout
