"""Compare caveman and pirate welcomes with a live llama.cpp model."""

# ruff: noqa: E402

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# This source path keeps the example runnable from a fresh clone before install.
SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from smallwords import is_compliant, make_resources, out_of_vocab, prompt_answer_simply
from smallwords._llama_server import generate_text, server_base_url

# This expected model keeps the example aligned with the other live examples.
MODEL_REPO = os.environ.get(
    "SMALLWORDS_LLAMA_MODEL",
    "bartowski/Qwen_Qwen3-8B-GGUF:q4_k_m",
)
# This server URL points the example at a running llama-server instance.
BASE_URL = server_base_url()
# This shared task keeps the two themed outputs easy to compare.
QUESTION_TEMPLATE = "Give a short {style}-style greeting for a new friend."
# This token budget leaves room for a short one-line welcome.
MAX_TOKENS = 48
# This slight temperature helps the example avoid instruction-parroting outputs.
TEMPERATURE = 0.2
# This deterministic seed keeps the example reproducible.
SEED = 7
# This key names the single response field in the matching JSON Schema.
SCHEMA_KEY = "reply"


@dataclass(frozen=True)
class WelcomeVariant:
    """Describe one themed welcome run for the comparison example."""

    label: str
    wordlist: str
    question: str


# These two variants compare the bundled themed remixes directly.
VARIANTS = (
    WelcomeVariant(
        label="Caveman",
        wordlist="caveman_898",
        question=QUESTION_TEMPLATE.format(style="caveman"),
    ),
    WelcomeVariant(
        label="Pirate",
        wordlist="pirate_898",
        question=QUESTION_TEMPLATE.format(style="pirate"),
    ),
)


def print_variant(variant: WelcomeVariant) -> None:
    """Print one constrained themed welcome run.

    Args:
        variant: The themed run configuration to execute.

    Returns:
        None.
    """
    resources = make_resources(variant.wordlist, max_words_per_line=12, max_lines=1)
    prompt = prompt_answer_simply(variant.question, wordlist=variant.wordlist)
    schema = resources.json_schema(
        key=SCHEMA_KEY,
        title=f"{variant.wordlist}_welcome",
    )
    request_summary = {
        "wordlist": variant.wordlist,
        "prompt": prompt,
        "seed": SEED,
        "temperature": TEMPERATURE,
        "n_predict": MAX_TOKENS,
        "schema_key": SCHEMA_KEY,
        "grammar_rule_count": resources.gbnf.count("::="),
    }
    pattern = schema["properties"][SCHEMA_KEY]["pattern"]
    response = generate_text(
        BASE_URL,
        prompt,
        grammar=resources.gbnf,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        seed=SEED,
    )

    print(f"=== {variant.label} Wordlist ===")
    print(variant.wordlist)
    print("=== Generation Request ===")
    print(json.dumps(request_summary, indent=2))
    print("=== Prompt ===")
    print(prompt)
    print("=== GBNF ===")
    print(resources.gbnf)
    print("=== JSON Schema ===")
    print(json.dumps(schema, indent=2))
    print("=== Model Response ===")
    print(response)
    print("=== Model Compliance ===")
    print(is_compliant(response, variant.wordlist))
    print("=== Model Schema Match ===")
    # The schema pattern is derived from the same limits as the bundled grammar.
    print(re.fullmatch(pattern, response) is not None)
    print("=== Model Out Of Vocab ===")
    print(out_of_vocab(response, variant.wordlist))


def main() -> None:
    """Print both themed prompts, resources, and live constrained responses.

    Returns:
        None.
    """
    print("=== Server ===")
    print(BASE_URL)
    print("=== Expected Model ===")
    print(MODEL_REPO)
    for index, variant in enumerate(VARIANTS):
        if index:
            print()
        print_variant(variant)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Keep failures concise when the script is used in docs or CI logs.
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
