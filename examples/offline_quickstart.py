"""Show the core smallwords workflow without a model server."""

from __future__ import annotations

import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from smallwords import OutputResources, OutputShape, allow_input_words
from smallwords.prompts import build_prompt


def main() -> None:
    """Build matching resources and check one sample response offline."""
    topic = "How does a bridge work?"
    spec = allow_input_words("basic_850", "bridge")
    shape = OutputShape(max_words_per_line=24, max_lines=1)
    resources = OutputResources.from_wordlist(spec, shape=shape)
    prompt = build_prompt("explain", topic, wordlist=spec)
    answer = "A bridge is a structure that helps people and things move across a river or a deep place."
    result = resources.validate(answer)

    print(prompt.splitlines()[0])
    print("GBNF rules:", resources.gbnf.count("::="))
    print("JSON Schema key:", next(iter(resources.json_schema()["properties"])))
    print("Sample valid:", result.valid)
    if result.issues:
        print("Issues:", "; ".join(result.issues))


if __name__ == "__main__":
    main()
