"""Reproduce the README bridge contrast with a live llama.cpp model."""

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
)
from smallwords.integrations import generate_text, server_base_url

# This expected model keeps the example aligned with the README contrast.
MODEL_REPO = os.environ.get(
    "SMALLWORDS_LLAMA_MODEL",
    "bartowski/Qwen_Qwen3-8B-GGUF:q4_k_m",
)
# This server URL points the example at a running llama-server instance.
BASE_URL = server_base_url()
# This is the shared plain-language bridge prompt used in both runs.
BASE_PROMPT = "Explain what a bridge does in one short sentence."
# This plain prompt drives the unconstrained comparison run.
STANDARD_PROMPT = BASE_PROMPT
# This topic feeds the opt-in task-word expansion helper.
TOPIC = "How does a bridge work?"
# This more expressive preset keeps the constrained answer readable.
BASE_WORDLIST = "basic_850"
# This derived spec adds the topic words back into the constrained vocabulary.
WORDLIST = allow_input_words(BASE_WORDLIST, TOPIC)
# This deterministic temperature keeps the README example reproducible.
TEMPERATURE = 0.0
# This deterministic seed keeps the README example reproducible.
SEED = 7
# This token budget leaves room for a single clean comparison sentence.
MAX_TOKENS = 32
# This resource bundle drives the constrained README example.
SMALLWORDS_RESOURCES = make_resources(WORDLIST, max_words_per_line=24, max_lines=1)
# This rendered word list is shown to the model inside the prompt.
SMALLWORDS_WORDS = ", ".join(WORDLIST.allowed_words())
# This constrained prompt keeps the wording close to the plain comparison prompt.
SMALLWORDS_PROMPT = (
    BASE_PROMPT
    + f" Use only words from the {BASE_WORDLIST} word list and the topic words shown below.\n"
    + f"Allowed words ({BASE_WORDLIST} + topic): {SMALLWORDS_WORDS}"
)
# This key names the single response field in the matching JSON Schema.
SCHEMA_KEY = "answer"
# This schema mirrors the same output limits as the grammar.
SMALLWORDS_SCHEMA = SMALLWORDS_RESOURCES.json_schema(
    key=SCHEMA_KEY,
    title="bridge_explanation",
)
# This plain request summary shows the unconstrained generation inputs.
STANDARD_REQUEST = {
    "prompt": STANDARD_PROMPT,
    "seed": SEED,
    "temperature": TEMPERATURE,
    "n_predict": MAX_TOKENS,
}
# This compact summary shows the combined constrained request shape.
SMALLWORDS_REQUEST = {
    "prompt": SMALLWORDS_PROMPT,
    "seed": SEED,
    "temperature": TEMPERATURE,
    "n_predict": MAX_TOKENS,
    "schema_key": SCHEMA_KEY,
    "grammar_rule_count": SMALLWORDS_RESOURCES.gbnf.count("::="),
}


def main() -> None:
    """Print the README's model-vs-wordlist bridge comparison.

    Returns:
        None.
    """
    print("=== Server ===")
    print(BASE_URL)
    print("=== Expected Model ===")
    print(MODEL_REPO)

    print("=== Standard Generation Request ===")
    print(json.dumps(STANDARD_REQUEST, indent=2))
    print("=== Standard Prompt ===")
    print(STANDARD_PROMPT)
    standard_answer = generate_text(
        BASE_URL,
        STANDARD_PROMPT,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        seed=SEED,
    )
    print("=== Standard Response ===")
    print(standard_answer)

    print("=== Smallwords Wordlist ===")
    print(f"{BASE_WORDLIST} + topic words")
    print("=== Smallwords Generation Request ===")
    print(json.dumps(SMALLWORDS_REQUEST, indent=2))
    print("=== Smallwords Prompt ===")
    print(SMALLWORDS_PROMPT)
    print("=== Smallwords GBNF ===")
    print(SMALLWORDS_RESOURCES.gbnf)
    print("=== Smallwords JSON Schema ===")
    print(json.dumps(SMALLWORDS_SCHEMA, indent=2))
    smallwords_answer = generate_text(
        BASE_URL,
        SMALLWORDS_PROMPT,
        grammar=SMALLWORDS_RESOURCES.gbnf,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        seed=SEED,
    )
    print("=== Smallwords Response ===")
    print(smallwords_answer)
    print("=== Smallwords Compliance ===")
    print(is_compliant(smallwords_answer, WORDLIST))
    print("=== Smallwords Schema Match ===")
    print(
        re.fullmatch(
            SMALLWORDS_SCHEMA["properties"][SCHEMA_KEY]["pattern"],
            smallwords_answer,
        )
        is not None
    )
    print("=== Smallwords Out Of Vocab ===")
    print(out_of_vocab(smallwords_answer, WORDLIST))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Keep failures concise when the script is used in docs or CI logs.
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
