"""Build portable resources for a simple bridge explanation."""

from __future__ import annotations

import json

from _shared import assert_response_matches_request, build_example_request
from smallwords import is_compliant, make_resources, out_of_vocab, prompt_explain_simply

WORDLIST = "common_250"


def main() -> None:
    """Print a bridge prompt, resources, and compliant sample explanation."""
    resources = make_resources(WORDLIST, max_words_per_line=9, max_lines=3)
    prompt = prompt_explain_simply("How does a bridge work?", wordlist=WORDLIST)
    request = build_example_request(
        prompt,
        resources,
        key="answer",
        title="bridge_explanation",
    )
    sample_reply = (
        "A way can go over water.\n"
        "Each part hold people up.\n"
        "The force move down through each side."
    )

    # Keep the sample reply self-validating so the example doubles as a guard.
    assert is_compliant(sample_reply, WORDLIST), out_of_vocab(sample_reply, WORDLIST)
    assert_response_matches_request(request, sample_reply)

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


if __name__ == "__main__":
    main()
