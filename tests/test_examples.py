"""Smoke tests for the example scripts shipped with the repository."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# This root path lets the smoke test execute the examples from the repo root.
ROOT = Path(__file__).resolve().parents[1]
# These are the lightweight examples that should always stay runnable.
EXAMPLES = [
    ROOT / "examples" / "customer_support_chat.py",
    ROOT / "examples" / "neighbor_intro_chat.py",
    ROOT / "examples" / "bridge_explain.py",
]


def test_examples_run() -> None:
    """Ensure the lightweight examples still execute from the repo root."""
    for example in EXAMPLES:
        completed = subprocess.run(
            [sys.executable, str(example)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        # Each example prints the same headings, which makes this a stable check.
        assert "=== Generation Request ===" in completed.stdout
        assert "=== Prompt ===" in completed.stdout
