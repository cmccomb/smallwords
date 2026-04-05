"""Build portable resources for a simple bridge explanation."""

from __future__ import annotations

import json

from _shared import build_example_request, response_matches_request
from smallwords import (
    allow_input_words,
    is_compliant,
    make_resources,
    out_of_vocab,
    prompt_explain_simply,
)

# This example starts from the compact common-word preset.
BASE_WORDLIST = "common_250"
# This topic is also added back into the allowed vocabulary for clarity.
TOPIC = "How does a bridge work?"


def main() -> None:
    """Print a bridge prompt, resources, and compliant sample explanation."""
    wordlist = allow_input_words(BASE_WORDLIST, TOPIC)
    resources = make_resources(wordlist, max_words_per_line=9, max_lines=3)
    prompt = prompt_explain_simply(TOPIC, wordlist=wordlist)
    request = build_example_request(
        prompt,
        resources,
        key="answer",
        title="bridge_explanation",
    )
    # Keep the sample hand-written so the script stays runnable without a model.
    sample_reply = (
        "A bridge goes over water.\n"
        "Each part holds people up.\n"
        "The force moves down through each side."
    )

    compliant = is_compliant(sample_reply, wordlist)
    request_match = response_matches_request(request, sample_reply)
    missing = out_of_vocab(sample_reply, wordlist)

    print("=== Generation Request ===")
    print(json.dumps(request.summary(), indent=2))
    print("=== Prompt ===")
    print(request.prompt)
    print("=== GBNF ===")
    print(request.grammar)
    print("=== JSON Schema ===")
    print(json.dumps(request.schema, indent=2))
    print("=== Sample Reply ===")
    print(sample_reply)
    print("=== Sample Compliance ===")
    print(compliant)
    print("=== Sample Request Match ===")
    print(request_match)
    print("=== Sample Out Of Vocab ===")
    print(missing)


if __name__ == "__main__":
    main()
