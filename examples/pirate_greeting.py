"""Generate one pirate-style greeting with a live llama.cpp model."""

# ruff: noqa: E402

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

# This source path keeps the example runnable from a fresh clone before install.
SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from smallwords import (
    WordlistSpec,
    get_wordlist,
    is_compliant,
    make_resources,
    out_of_vocab,
)
from smallwords.integrations import generate_text, server_base_url

# This expected model keeps the example aligned with the other live examples.
MODEL_REPO = os.environ.get(
    "SMALLWORDS_LLAMA_MODEL",
    "bartowski/Qwen_Qwen3-8B-GGUF:q4_k_m",
)
# This server URL points the example at a running llama-server instance.
BASE_URL = server_base_url()
# This built-in themed list anchors the focused pirate greeting vocabulary below.
BASE_WORDLIST = get_wordlist("pirate_898")
# This compact surface-word set is selected from `pirate_898` for a quick live demo.
FOCUSED_SURFACE_WORDS = tuple(
    word
    for word in ("ahoy", "matey", "good", "to", "meet", "you")
    if word in BASE_WORDLIST.allowed_words()
)
# This focused spec keeps the pirate example playful without a giant word block.
PIRATE_WORDLIST = WordlistSpec(
    name="pirate_898_greeting_focus",
    words=FOCUSED_SURFACE_WORDS,
    description="A focused pirate greeting vocabulary selected from pirate_898 for the example script.",
    source_name="Selected surface forms from pirate_898 for the pirate greeting example",
    source_urls=BASE_WORDLIST.source_urls,
    license_name=BASE_WORDLIST.license_name,
    allowed_punctuation=(".",),
    variant_mode="surface_only",
)
# This task asks for a complete pirate greeting instead of a clipped phrase.
TASK = (
    "A pirate meets a new friend on a ship. Write one short friendly greeting "
    "sentence. Use exactly 6 words and make it sound complete."
)
# This prompt spells out the allowed words so the model can see the constraint directly.
PROMPT = (
    f"{TASK}\n\n"
    f"Allowed words ({PIRATE_WORDLIST.name}): {', '.join(PIRATE_WORDLIST.allowed_words())}\n"
)
# This resource bundle keeps the response to one compact sentence.
RESOURCES = make_resources(
    PIRATE_WORDLIST,
    min_words_per_line=6,
    max_words_per_line=6,
    max_lines=1,
)
# This token budget leaves room for one short pirate greeting sentence.
MAX_TOKENS = 24
# This deterministic temperature keeps the example reproducible.
TEMPERATURE = 0.0
# This deterministic seed keeps the example reproducible.
SEED = 7
# This key names the single response field in the matching JSON Schema.
SCHEMA_KEY = "reply"
# This schema mirrors the same output limits as the grammar.
SCHEMA = RESOURCES.json_schema(key=SCHEMA_KEY, title="pirate_greeting")
# This compact summary shows the combined request shape without extra helper code.
REQUEST_SUMMARY = {
    "wordlist": PIRATE_WORDLIST.name,
    "prompt": PROMPT,
    "seed": SEED,
    "temperature": TEMPERATURE,
    "n_predict": MAX_TOKENS,
    "schema_key": SCHEMA_KEY,
    "grammar_rule_count": RESOURCES.gbnf.count("::="),
}


def main() -> None:
    """Print the pirate prompt, resources, and a live constrained response.

    Returns:
        None.
    """
    pattern = SCHEMA["properties"][SCHEMA_KEY]["pattern"]
    response = generate_text(
        BASE_URL,
        PROMPT,
        grammar=RESOURCES.gbnf,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        seed=SEED,
    )

    print("=== Server ===")
    print(BASE_URL)
    print("=== Expected Model ===")
    print(MODEL_REPO)
    print("=== Wordlist ===")
    print(PIRATE_WORDLIST.name)
    print("=== Generation Request ===")
    print(json.dumps(REQUEST_SUMMARY, indent=2))
    print("=== Prompt ===")
    print(PROMPT)
    print("=== GBNF ===")
    print(RESOURCES.gbnf)
    print("=== JSON Schema ===")
    print(json.dumps(SCHEMA, indent=2))
    print("=== Model Response ===")
    print(response)
    print("=== Model Compliance ===")
    print(is_compliant(response, PIRATE_WORDLIST))
    print("=== Model Schema Match ===")
    # The schema pattern is derived from the same limits as the bundled grammar.
    print(re.fullmatch(pattern, response) is not None)
    print("=== Model Out Of Vocab ===")
    print(out_of_vocab(response, PIRATE_WORDLIST))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Keep failures concise when the script is used in docs or CI logs.
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
