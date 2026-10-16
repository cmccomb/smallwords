"""Generate the README's six controlled-vocabulary missile rewrites."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from _shared import generate_text, server_base_url
from smallwords import (
    OutputResources,
    OutputShape,
    WordlistSpec,
    allow_input_words,
    get_wordlist,
    validate_output,
)
from smallwords.prompts import build_prompt

MODEL_REPO = os.environ.get(
    "SMALLWORDS_LLAMA_MODEL",
    "ibm-granite/granite-4.2-8b-GGUF:Q4_K_M",
)
BASE_URL = server_base_url()
SOURCE = (
    "The missile knows where it is at all times. "
    "By subtracting where it is from where it isn't, or where it isn't from "
    "where it is, it obtains a difference, or deviation."
)
SHAPE = OutputShape(min_words_per_line=6, max_words_per_line=11, max_lines=3)
MAX_TOKENS = 128
TEMPERATURE = 0.55


@dataclass(frozen=True)
class ContrastCase:
    """Hold one focused generation case and its full validation preset."""

    label: str
    full_wordlist: WordlistSpec
    focused_wordlist: WordlistSpec
    instruction: str
    seed: int


def focused_wordlist(
    name: str,
    full_wordlist: WordlistSpec,
    words: str,
) -> WordlistSpec:
    """Select a compact surface vocabulary from a complete preset."""
    allowed = set(full_wordlist.allowed_words())
    selected = tuple(word for word in words.split() if word in allowed)
    return WordlistSpec(
        name=name,
        words=selected,
        description=f"A task-focused subset of {full_wordlist.name}.",
        source_name=f"Selected surface forms from {full_wordlist.name}",
        source_urls=full_wordlist.source_urls,
        license_name=full_wordlist.license_name,
        allowed_punctuation=(".",),
        variant_mode="surface_only",
        style_hint=full_wordlist.style_hint,
    )


SIMPLE_FULL = allow_input_words("moby_898", "missile")
CAVEMAN_FULL = get_wordlist("caveman_898")
BASIC_FULL = get_wordlist("basic_850")
SPECIAL_FULL = get_wordlist("special_english_1475")
PIRATE_FULL = get_wordlist("pirate_898")
COWBOY_FULL = get_wordlist("cowboy_898")
CASES = (
    ContrastCase(
        label="Simple",
        full_wordlist=SIMPLE_FULL,
        focused_wordlist=focused_wordlist(
            "simple_position_focus",
            SIMPLE_FULL,
            "the missile knows where it is at all times now should be next "
            "difference tells how far to move",
        ),
        instruction=(
            "Explain in exactly three short sentences. Sentence one says the "
            "missile knows where it is at all times. Sentence two says it knows "
            "where it should be next. Sentence three says the difference tells "
            "it how far to move. Begin the sentences with 'The missile knows', "
            "'It knows', and 'The difference'."
        ),
        seed=3,
    ),
    ContrastCase(
        label="Caveman",
        full_wordlist=CAVEMAN_FULL,
        focused_wordlist=focused_wordlist(
            "caveman_position_focus",
            CAVEMAN_FULL,
            "rock know where it be now here should there far tell how "
            "must go from to at",
        ),
        instruction=(
            "Explain in exactly three short, rough caveman sentences. Use a rock "
            "as the thing that moves. Sentence one says rock knows where it is "
            "now. Sentence two says rock knows where it should be. Sentence three "
            "says rock knows how far it must go. Begin each sentence with "
            "'Rock know'."
        ),
        seed=4,
    ),
    ContrastCase(
        label="Basic",
        full_wordlist=BASIC_FULL,
        focused_wordlist=focused_wordlist(
            "basic_position_focus",
            BASIC_FULL,
            "the thing has knowledge of where is now be how far to move "
            "other place there here from at distance",
        ),
        instruction=(
            "Explain in exactly three short sentences. Sentence one says the "
            "thing has knowledge of where the thing is now. Sentence two says "
            "the thing is to be at the other place. Sentence three says the "
            "distance from here to there is how far to move. Begin the sentences "
            "with 'The thing has', 'The thing is to', and 'The distance'."
        ),
        seed=5,
    ),
    ContrastCase(
        label="Special",
        full_wordlist=SPECIAL_FULL,
        focused_wordlist=focused_wordlist(
            "special_position_focus",
            SPECIAL_FULL,
            "the missile knows where it is at all times now should be first "
            "second place distance tells how far to move from there here",
        ),
        instruction=(
            "Explain in exactly three short sentences. Sentence one says the "
            "missile knows where it is at all times. Sentence two says it "
            "should be at the second place. Sentence three says the distance "
            "tells how far to move from here to there. Begin the sentences "
            "with 'The missile knows', 'It should', and 'The distance'."
        ),
        seed=7,
    ),
    ContrastCase(
        label="Pirate",
        full_wordlist=PIRATE_FULL,
        focused_wordlist=focused_wordlist(
            "pirate_position_focus",
            PIRATE_FULL,
            "the ship knows where it is now at all times crew should be "
            "difference tells which way to sail",
        ),
        instruction=(
            "Explain in exactly three short pirate sentences. Sentence one says "
            "the ship knows where it is now. Sentence two says the crew knows "
            "where the ship should be. Sentence three says the difference tells "
            "the crew which way to sail. Begin the sentences with 'The ship "
            "knows', 'The crew knows', and 'The difference'."
        ),
        seed=6,
    ),
    ContrastCase(
        label="Cowboy",
        full_wordlist=COWBOY_FULL,
        focused_wordlist=focused_wordlist(
            "cowboy_position_focus",
            COWBOY_FULL,
            "the cowboy knows where cattle are now ranch is should be difference "
            "tells which way to ride",
        ),
        instruction=(
            "Explain in exactly three short cowboy sentences. Sentence one says "
            "the cowboy knows where the cattle are now. Sentence two says the "
            "ranch is where the cattle should be. Sentence three says the "
            "difference tells the cowboy which way to ride. Begin the sentences "
            "with 'The cowboy knows', 'The ranch is', and 'The difference'."
        ),
        seed=0,
    ),
)


def generate_case(case: ContrastCase) -> None:
    """Generate and report one constrained rewrite."""
    resources = OutputResources.from_wordlist(case.focused_wordlist, shape=SHAPE)
    schema_key = case.label.lower()
    schema = resources.json_schema(
        key=schema_key,
        title=f"{schema_key}_missile_rewrite",
    )
    prompt = (
        build_prompt("explain", SOURCE, wordlist=case.focused_wordlist)
        + "\nWrite exactly three lines. Put one complete sentence on each line.\n"
        + case.instruction
        + "\n"
    )
    request = {
        "focused_wordlist": case.focused_wordlist.name,
        "full_validation_wordlist": case.full_wordlist.name,
        "shape": asdict(SHAPE),
        "seed": case.seed,
        "temperature": TEMPERATURE,
        "n_predict": MAX_TOKENS,
        "cache_prompt": False,
        "schema_key": schema_key,
        "grammar_rule_count": resources.gbnf.count("::="),
    }
    response = generate_text(
        BASE_URL,
        prompt,
        grammar=resources.gbnf,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        seed=case.seed,
    )
    focused_result = validate_output(
        response,
        case.focused_wordlist,
        shape=SHAPE,
    )
    full_result = validate_output(response, case.full_wordlist, shape=SHAPE)

    print(f"=== {case.label} Generation Request ===")
    print(json.dumps(request, indent=2))
    print(f"=== {case.label} Prompt ===")
    print(prompt)
    print(f"=== {case.label} GBNF ===")
    print(resources.gbnf)
    print(f"=== {case.label} JSON Schema ===")
    print(json.dumps(schema, indent=2))
    print(f"=== {case.label} Model Response ===")
    print(response)
    print(f"=== {case.label} Focused Validation ===")
    print(json.dumps(asdict(focused_result), indent=2))
    print(f"=== {case.label} Full Preset Validation ===")
    print(json.dumps(asdict(full_result), indent=2))


def main() -> None:
    """Print the source and all six live constrained rewrites."""
    print("=== Server ===")
    print(BASE_URL)
    print("=== Expected Model ===")
    print(MODEL_REPO)
    print("=== Original ===")
    print(SOURCE)
    for case in CASES:
        generate_case(case)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
