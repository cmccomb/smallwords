"""Reproduce the README bridge contrast with local llama.cpp and Qwen."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys

from _shared import assert_response_matches_request, build_example_request
from smallwords import (
    is_compliant,
    make_resources,
    out_of_vocab,
    prompt_explain_simply,
)

MODEL_REPO = os.environ.get(
    "SMALLWORDS_LLAMA_MODEL",
    "bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF:q4_k_m",
)

STANDARD_PROMPT = "Explain how a bridge works in exactly three short sentences."
WORDLIST = "common_250"
SMALLWORDS_RESOURCES = make_resources(WORDLIST, max_words_per_line=9, max_lines=3)
SMALLWORDS_PROMPT = prompt_explain_simply("How does a bridge work?", wordlist=WORDLIST)
SMALLWORDS_REQUEST = build_example_request(
    SMALLWORDS_PROMPT,
    SMALLWORDS_RESOURCES,
    key="answer",
    title="bridge_explanation",
)
SMALLWORDS_REFERENCE = (
    "A way goes over water.\n"
    "Each part hold people up.\n"
    "The force move down through each side."
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


def _extract_answer(raw_output: str, prompt: str) -> str:
    """Extract the generated answer body from a llama.cpp transcript."""
    text = _clean_terminal_output(raw_output)
    anchor = f"> {prompt}"
    if anchor not in text:
        raise RuntimeError(
            f"Could not find prompt anchor in llama.cpp output for: {prompt!r}"
        )

    answer = text.split(anchor, 1)[1].strip()
    for marker in ("llama_memory_breakdown_print:", "[ Prompt:", "Exiting..."):
        if marker in answer:
            answer = answer.split(marker, 1)[0].strip()
    return " ".join(line.strip() for line in answer.splitlines() if line.strip())


def _run_prompt(prompt: str, *, seed: int) -> str:
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
        "0",
        "-n",
        "96",
        "-p",
        prompt,
    ]

    env = dict(os.environ)
    env["TERM"] = "dumb"

    completed = subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )
    return _extract_answer(completed.stdout, prompt)


def main() -> None:
    """Print the README's model-vs-wordlist bridge comparison."""
    assert_response_matches_request(SMALLWORDS_REQUEST, SMALLWORDS_REFERENCE)

    print("=== Model ===")
    print(MODEL_REPO)

    print("=== Standard Prompt ===")
    print(STANDARD_PROMPT)
    standard_answer = _run_prompt(STANDARD_PROMPT, seed=7)
    print("=== Standard Response ===")
    print(standard_answer)

    print("=== Smallwords Wordlist ===")
    print(WORDLIST)
    print("=== Smallwords Generation Request ===")
    print(json.dumps(SMALLWORDS_REQUEST.summary(), indent=2))
    print("=== Smallwords Prompt ===")
    print(SMALLWORDS_REQUEST.prompt)
    print("=== Smallwords GBNF ===")
    print(SMALLWORDS_REQUEST.grammar)
    print("=== Smallwords Reference Response ===")
    print(SMALLWORDS_REFERENCE)
    print("=== Reference Compliance ===")
    print(is_compliant(SMALLWORDS_REFERENCE, WORDLIST))
    print("=== Reference Out Of Vocab ===")
    print(out_of_vocab(SMALLWORDS_REFERENCE, WORDLIST))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Keep failures concise when the script is used in docs or CI logs.
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
