"""Reproduce the README bridge contrast with a live llama.cpp model."""

# ruff: noqa: E402

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import asdict
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from _shared import generate_text, server_base_url
from smallwords import (
    OutputResources,
    OutputShape,
    allow_input_words,
    is_compliant,
    out_of_vocab,
)
from smallwords.prompts import build_prompt

MODEL_REPO = os.environ.get(
    "SMALLWORDS_LLAMA_MODEL",
    "bartowski/Qwen_Qwen3-8B-GGUF:q4_k_m",
)
BASE_URL = server_base_url()
BASE_PROMPT = "Explain what a bridge does in one short sentence."
STANDARD_PROMPT = BASE_PROMPT
TOPIC = "How does a bridge work?"
WORDLIST = allow_input_words("basic_850", TOPIC)
SHAPE = OutputShape(max_words_per_line=24, max_lines=1)
TEMPERATURE = 0.0
SEED = 7
MAX_TOKENS = 32
RESOURCES = OutputResources.from_wordlist(WORDLIST, shape=SHAPE)
PROMPT = build_prompt("explain", TOPIC, wordlist=WORDLIST)
SCHEMA_KEY = "answer"
SCHEMA = RESOURCES.json_schema(key=SCHEMA_KEY, title="bridge_explanation")
STANDARD_REQUEST = {
    "prompt": STANDARD_PROMPT,
    "seed": SEED,
    "temperature": TEMPERATURE,
    "n_predict": MAX_TOKENS,
}
SMALLWORDS_REQUEST = {
    "wordlist": WORDLIST.name,
    "shape": asdict(SHAPE),
    "seed": SEED,
    "temperature": TEMPERATURE,
    "n_predict": MAX_TOKENS,
    "schema_key": SCHEMA_KEY,
    "grammar_rule_count": RESOURCES.gbnf.count("::="),
}


def main() -> None:
    """Print the README's model-vs-wordlist bridge comparison."""
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
    print(WORDLIST.name)
    print("=== Smallwords Resource Shape ===")
    print(json.dumps(SMALLWORDS_REQUEST["shape"], indent=2))
    print("=== Smallwords Generation Request ===")
    print(json.dumps(SMALLWORDS_REQUEST, indent=2))
    print("=== Smallwords Prompt ===")
    print(PROMPT)
    print("=== Smallwords GBNF ===")
    print(RESOURCES.gbnf)
    print("=== Smallwords JSON Schema ===")
    print(json.dumps(SCHEMA, indent=2))
    smallwords_answer = generate_text(
        BASE_URL,
        PROMPT,
        grammar=RESOURCES.gbnf,
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
            SCHEMA["properties"][SCHEMA_KEY]["pattern"],
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
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
