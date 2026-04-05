"""Build portable resources for a simple customer-support reply."""

from __future__ import annotations

import json

from _shared import assert_response_matches_request, build_example_request
from smallwords import is_compliant, make_resources, out_of_vocab, prompt_answer_simply

WORDLIST = "reasoning_250"


def main() -> None:
    """Print a support-oriented prompt, resources, and compliant sample reply."""
    resources = make_resources(WORDLIST, max_words_per_line=8, max_lines=3)
    prompt = prompt_answer_simply(
        "My order is late. What can I do now?", wordlist=WORDLIST
    )
    request = build_example_request(
        prompt,
        resources,
        key="reply",
        title="support_reply",
    )
    sample_reply = (
        "Ask for help now.\n"
        "Tell the story in a clear way.\n"
        "Make a plan for the next step."
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
