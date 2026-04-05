"""Build portable resources for a simple bridge explanation."""

from __future__ import annotations

import json

from smallwords import is_compliant, make_resources, out_of_vocab, prompt_explain_simply

WORDLIST = "common_250"


def main() -> None:
    resources = make_resources(WORDLIST, max_words_per_line=9, max_lines=3)
    prompt = prompt_explain_simply("How does a bridge work?", wordlist=WORDLIST)
    sample_reply = (
        "A way can go over water.\n"
        "Each part hold people up.\n"
        "The force move down through each side."
    )

    assert is_compliant(sample_reply, WORDLIST), out_of_vocab(sample_reply, WORDLIST)

    print("=== Prompt ===")
    print(prompt)
    print("=== GBNF ===")
    print(resources.gbnf)
    print("=== JSON Schema ===")
    print(json.dumps(resources.json_schema(key="answer", title="bridge_explanation"), indent=2))
    print("=== Sample Reply ===")
    print(sample_reply)


if __name__ == "__main__":
    main()
