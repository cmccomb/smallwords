"""Reproduce the README bridge contrast with local llama.cpp and Qwen."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

from _shared import build_example_request, response_matches_request
from smallwords import (
    allow_input_words,
    is_compliant,
    make_resources,
    out_of_vocab,
)

MODEL_REPO = os.environ.get(
    "SMALLWORDS_LLAMA_MODEL",
    "bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF:q4_k_m",
)

BASE_PROMPT = "Explain what a bridge does in one short sentence."
STANDARD_PROMPT = BASE_PROMPT
TOPIC = "How does a bridge work?"
BASE_WORDLIST = "basic_850"
WORDLIST = allow_input_words(BASE_WORDLIST, TOPIC)
TEMPERATURE = 0.0
MAX_TOKENS = 96
SMALLWORDS_RESOURCES = make_resources(WORDLIST, max_words_per_line=24, max_lines=1)
SMALLWORDS_WORDS = ", ".join(WORDLIST.allowed_words())
SMALLWORDS_PROMPT = (
    BASE_PROMPT
    + f" Use only words from the {BASE_WORDLIST} word list and the topic words shown below.\n"
    + f"Allowed words ({BASE_WORDLIST} + topic): {SMALLWORDS_WORDS}"
)
SMALLWORDS_REQUEST = build_example_request(
    SMALLWORDS_PROMPT,
    SMALLWORDS_RESOURCES,
    key="answer",
    title="bridge_explanation",
)


def _clean_terminal_output(text: str) -> str:
    """Strip terminal control noise from llama.cpp output."""
    text = text.replace("\r", "")
    text = re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", text)

    # Some terminals emit backspace redraw sequences instead of ANSI escapes.
    previous = None
    while previous != text:
        previous = text
        text = re.sub(r".\x08", "", text)

    return text


def _extract_answer(
    raw_output: str, prompt: str, *, preserve_newlines: bool = False
) -> str:
    """Extract the generated answer body from a llama.cpp transcript."""
    text = _clean_terminal_output(raw_output)
    anchor = f"> {prompt}"
    if anchor in text:
        answer = text.split(anchor, 1)[1].strip()
    else:
        # Long prompts may be visually truncated by llama.cpp in the transcript.
        prompt_start = text.rfind("\n> ")
        if prompt_start == -1:
            prompt_start = text.find("> ")
        if prompt_start == -1:
            raise RuntimeError(
                f"Could not find prompt anchor in llama.cpp output for: {prompt!r}"
            )

        prompt_block = text[prompt_start:].strip()
        parts = re.split(r"\n\s*\n", prompt_block, maxsplit=1)
        if len(parts) != 2:
            raise RuntimeError(
                f"Could not isolate answer block in llama.cpp output for: {prompt!r}"
            )
        answer = parts[1].strip()

    for marker in ("llama_memory_breakdown_print:", "[ Prompt:", "Exiting..."):
        if marker in answer:
            answer = answer.split(marker, 1)[0].strip()
    lines = [line.strip() for line in answer.splitlines() if line.strip()]
    if preserve_newlines:
        return "\n".join(lines)
    return " ".join(lines)


def _run_prompt(
    prompt: str,
    *,
    seed: int,
    grammar: str | None = None,
    max_tokens: int = 96,
    temperature: float = 0.0,
    preserve_newlines: bool = False,
) -> str:
    """Run one prompt through llama.cpp and return the cleaned answer text."""
    llama_cli = shutil.which("llama-cli")
    if not llama_cli:
        raise RuntimeError("llama-cli is not installed or not on PATH.")

    command = [
        llama_cli,
        "-hf",
        MODEL_REPO,
        "--reasoning-budget",
        "0",
        "--single-turn",
        "--no-display-prompt",
        "--no-show-timings",
        "--seed",
        str(seed),
        "--temp",
        str(temperature),
        "-n",
        str(max_tokens),
        "-p",
        prompt,
    ]

    grammar_path: str | None = None
    if grammar is not None:
        # llama.cpp wants a file path for larger grammars, so write one briefly.
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", suffix=".gbnf", delete=False
        ) as handle:
            handle.write(grammar)
            grammar_path = handle.name
        command.extend(["--grammar-file", grammar_path])

    env = dict(os.environ)
    env["TERM"] = "dumb"

    try:
        completed = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
        )
    finally:
        if grammar_path and os.path.exists(grammar_path):
            os.unlink(grammar_path)

    return _extract_answer(
        completed.stdout,
        prompt,
        preserve_newlines=preserve_newlines,
    )


def main() -> None:
    """Print the README's model-vs-wordlist bridge comparison."""
    print("=== Model ===")
    print(MODEL_REPO)

    print("=== Standard Prompt ===")
    print(STANDARD_PROMPT)
    standard_answer = _run_prompt(
        STANDARD_PROMPT,
        seed=7,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )
    print("=== Standard Response ===")
    print(standard_answer)

    print("=== Smallwords Wordlist ===")
    print(f"{BASE_WORDLIST} + topic words")
    print("=== Smallwords Generation Request ===")
    print(json.dumps(SMALLWORDS_REQUEST.summary(), indent=2))
    print("=== Smallwords Prompt ===")
    print(SMALLWORDS_REQUEST.prompt)
    print("=== Smallwords GBNF ===")
    print(SMALLWORDS_REQUEST.grammar)
    smallwords_answer = _run_prompt(
        SMALLWORDS_REQUEST.prompt,
        seed=7,
        grammar=SMALLWORDS_REQUEST.grammar,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        preserve_newlines=True,
    )
    print("=== Smallwords Response ===")
    print(smallwords_answer)
    print("=== Smallwords Compliance ===")
    print(is_compliant(smallwords_answer, WORDLIST))
    print("=== Smallwords Request Match ===")
    print(response_matches_request(SMALLWORDS_REQUEST, smallwords_answer))
    print("=== Smallwords Out Of Vocab ===")
    print(out_of_vocab(smallwords_answer, WORDLIST))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Keep failures concise when the script is used in docs or CI logs.
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
