"""Show the themed presets and validate sample lines without a model."""

from __future__ import annotations

import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from smallwords import OutputResources
from smallwords.prompts import build_prompt

SAMPLES = (
    (
        "pirate_898",
        "Ahoy matey the crew will sail to the island for gold.",
    ),
    (
        "cowboy_898",
        "Howdy friend the cattle are on the trail near my ranch.",
    ),
)


def main() -> None:
    """Print each preset's guidance and a valid sample line."""
    for name, sample in SAMPLES:
        resources = OutputResources.from_wordlist(name)
        prompt = build_prompt(
            "answer", "Greet a friend and describe the day.", wordlist=name
        )
        print(name)
        print("Prompt:", prompt.splitlines()[0])
        print("Sample:", sample)
        print("Valid:", resources.validate(sample).valid)


if __name__ == "__main__":
    main()
