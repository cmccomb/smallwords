"""Build portable resources for a friendly small-talk reply."""

from __future__ import annotations

import json

from smallwords import is_compliant, make_resources, out_of_vocab, prompt_answer_simply

WORDLIST = "common_250"


def main() -> None:
    """Print a small-talk prompt, resources, and compliant sample reply."""
    resources = make_resources(WORDLIST, max_words_per_line=8, max_lines=3)
    prompt = prompt_answer_simply(
        "Write a short friendly reply when you meet a new neighbor.",
        wordlist=WORDLIST,
    )
    sample_reply = (
        "Good day.\nI feel good to see new people.\nThis place can feel like home."
    )

    # Keep the sample reply self-validating so the example doubles as a guard.
    assert is_compliant(sample_reply, WORDLIST), out_of_vocab(sample_reply, WORDLIST)

    print("=== Prompt ===")
    print(prompt)
    print("=== GBNF ===")
    print(resources.gbnf)
    print("=== JSON Schema ===")
    print(
        json.dumps(resources.json_schema(key="reply", title="neighbor_reply"), indent=2)
    )
    print("=== Sample Reply ===")
    print(sample_reply)


if __name__ == "__main__":
    main()
