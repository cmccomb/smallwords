"""Rewrite a technical passage with a live llama.cpp model and grammar."""

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
    allow_input_words,
    is_compliant,
    make_resources,
    out_of_vocab,
    prompt_rewrite_simply,
)
from smallwords.integrations import generate_text, server_base_url

# This expected model keeps the example aligned with the README contrast.
MODEL_REPO = os.environ.get(
    "SMALLWORDS_LLAMA_MODEL",
    "bartowski/Qwen_Qwen3-8B-GGUF:q4_k_m",
)
# This server URL points the example at a running llama-server instance.
BASE_URL = server_base_url()
# This source-backed base list leaves room for readable simplified technical prose.
BASE_WORDLIST = "special_english_1475"
# This passage is intentionally technical so the example shows a real simplification task.
SOURCE_PASSAGE = (
    "The navigation stack estimates the robot position by combining wheel "
    "encoder readings, inertial measurements, and camera landmarks several "
    "times each second."
)
# This derived spec adds the passage terms so the model can refer to them when needed.
WORDLIST = allow_input_words(BASE_WORDLIST, SOURCE_PASSAGE)
# This resource bundle keeps the example to one readable sentence.
RESOURCES = make_resources(WORDLIST, max_words_per_line=16, max_lines=1)
# This prompt pairs the source passage with the explicit allowed vocabulary.
PROMPT = prompt_rewrite_simply(SOURCE_PASSAGE, wordlist=WORDLIST)
# This token budget leaves room for one complete simplified sentence.
MAX_TOKENS = 72
# This slight temperature helps the example avoid instruction-parroting outputs.
TEMPERATURE = 0.2
# This deterministic seed keeps the example reproducible.
SEED = 7
# This key names the single response field in the matching JSON Schema.
SCHEMA_KEY = "rewrite"
# This schema mirrors the same output limits as the grammar.
SCHEMA = RESOURCES.json_schema(key=SCHEMA_KEY, title="technical_rewrite")
# This compact summary shows the combined request shape without extra helper code.
REQUEST_SUMMARY = {
    "prompt": PROMPT,
    "seed": SEED,
    "temperature": TEMPERATURE,
    "n_predict": MAX_TOKENS,
    "schema_key": SCHEMA_KEY,
    "grammar_rule_count": RESOURCES.gbnf.count("::="),
}


def main() -> None:
    """Print the rewrite prompt, resources, and a live constrained response.

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
    print("=== Source Passage ===")
    print(SOURCE_PASSAGE)
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
    print(is_compliant(response, WORDLIST))
    print("=== Model Schema Match ===")
    # The schema pattern is derived from the same limits as the bundled grammar.
    print(re.fullmatch(pattern, response) is not None)
    print("=== Model Out Of Vocab ===")
    print(out_of_vocab(response, WORDLIST))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Keep failures concise when the script is used in docs or CI logs.
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
