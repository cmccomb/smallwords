"""Rewrite a technical passage with a live llama.cpp model and grammar."""

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
    WordlistSpec,
    get_wordlist,
    is_compliant,
    out_of_vocab,
)
from smallwords.prompts import build_prompt

MODEL_REPO = os.environ.get(
    "SMALLWORDS_LLAMA_MODEL",
    "bartowski/Qwen_Qwen3-8B-GGUF:q4_k_m",
)
BASE_URL = server_base_url()
BASE_WORDLIST = get_wordlist("basic_850")
SOURCE_PASSAGE = (
    "The thermal controller derates propulsion output after the sensor array "
    "reports an overtemperature fault."
)
FOCUSED_CANONICAL_WORDS = tuple(
    word
    for word in BASE_WORDLIST.canonical_words()
    if word
    in {
        "be",
        "cut",
        "engine",
        "heat",
        "high",
        "if",
        "power",
        "system",
        "this",
        "very",
        "when",
    }
)
WORDLIST = WordlistSpec(
    name="basic_850_rewrite_focus",
    words=FOCUSED_CANONICAL_WORDS,
    description="A focused rewrite vocabulary selected from basic_850 for the example script.",
    source_name="Selected from basic_850 for the rewrite example",
    source_urls=BASE_WORDLIST.source_urls,
    license_name=BASE_WORDLIST.license_name,
    allowed_punctuation=(".",),
)
SHAPE = OutputShape(min_words_per_line=10, max_words_per_line=10, max_lines=1)
RESOURCES = OutputResources.from_wordlist(WORDLIST, shape=SHAPE)
PROMPT = build_prompt("rewrite", SOURCE_PASSAGE, wordlist=WORDLIST)
MAX_TOKENS = 96
TEMPERATURE = 0.0
SEED = 7
SCHEMA_KEY = "rewrite"
SCHEMA = RESOURCES.json_schema(key=SCHEMA_KEY, title="technical_rewrite")
REQUEST_SUMMARY = {
    "wordlist": WORDLIST.name,
    "shape": asdict(SHAPE),
    "seed": SEED,
    "temperature": TEMPERATURE,
    "n_predict": MAX_TOKENS,
    "schema_key": SCHEMA_KEY,
    "grammar_rule_count": RESOURCES.gbnf.count("::="),
}


def main() -> None:
    """Print the rewrite prompt, resources, and a live constrained response."""
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
    print("=== Resource Shape ===")
    print(json.dumps(REQUEST_SUMMARY["shape"], indent=2))
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
    print(re.fullmatch(pattern, response) is not None)
    print("=== Model Out Of Vocab ===")
    print(out_of_vocab(response, WORDLIST))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
