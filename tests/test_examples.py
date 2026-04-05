"""Smoke tests for the example scripts shipped with the repository."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = [
    ROOT / "examples" / "readme_bridge_contrast.py",
    ROOT / "examples" / "pirate_greeting.py",
    ROOT / "examples" / "rewrite_technical_passage.py",
]


def test_example_files_exist() -> None:
    """Ensure the expected example files stay present in the repository."""
    for example in EXAMPLES:
        assert example.exists()
    assert (ROOT / "examples" / "_shared.py").exists()


@pytest.mark.skipif(
    os.environ.get("SMALLWORDS_RUN_LIVE_EXAMPLES") != "1",
    reason="Live llama.cpp example runs are opt-in outside local verification.",
)
def test_examples_run() -> None:
    """Ensure the live examples still execute from the repo root when enabled."""
    for example in EXAMPLES:
        completed = subprocess.run(
            [sys.executable, str(example)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        assert "=== Server ===" in completed.stdout
        assert (
            "=== Generation Request ===" in completed.stdout
            or "=== Standard Generation Request ===" in completed.stdout
        )
