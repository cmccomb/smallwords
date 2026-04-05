"""Build portable resources for a simple customer-support reply."""

from __future__ import annotations

import json

from _shared import build_example_request, response_matches_request
from smallwords import (
    allow_input_words,
    is_compliant,
    make_resources,
    out_of_vocab,
    prompt_answer_simply,
)

BASE_WORDLIST = "reasoning_250"
QUESTION = "My order is late. What can I do now?"


def main() -> None:
    """Print a support-oriented prompt, resources, and compliant sample reply."""
    wordlist = allow_input_words(BASE_WORDLIST, QUESTION)
    resources = make_resources(wordlist, max_words_per_line=8, max_lines=3)
    prompt = prompt_answer_simply(QUESTION, wordlist=wordlist)
    request = build_example_request(
        prompt,
        resources,
        key="reply",
        title="support_reply",
    )
    # The sample shows the kind of short, stepwise support reply the prompt asks for.
    sample_reply = (
        "Ask about the order now.\n"
        "Tell the story in a clear way.\n"
        "Make a plan for the next step."
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
