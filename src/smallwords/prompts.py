"""Build prompt text that stays aligned with the active vocabulary."""

from __future__ import annotations

from typing import Literal

from ._spec_utils import resolve_wordlist_spec
from .types import WordlistSpec

PromptKind = Literal["answer", "explain", "rewrite", "summarize"]

_PROMPT_SPECS: dict[PromptKind, tuple[str, str, str]] = {
    "answer": (
        "Answer the question in plain English. Use only words from the {name} word list. "
        "Be direct, brief, and clear.",
        "Question",
        "answer",
    ),
    "explain": (
        "Explain the topic in plain English. Use only words from the {name} word list. "
        "Use short sentences and concrete language.",
        "Topic",
        "answer",
    ),
    "rewrite": (
        "Rewrite the text in plain English. Use only words from the {name} word list. "
        "Keep the meaning, but make the wording easier.",
        "Text",
        "rewrite",
    ),
    "summarize": (
        "Summarize the text in plain English. Use only words from the {name} word list. "
        "Keep the key points and cut extra detail.",
        "Text",
        "summary",
    ),
}


def build_prompt(
    kind: PromptKind,
    content: str,
    *,
    wordlist: str | WordlistSpec = "basic_850",
    thinking: bool = False,
) -> str:
    """Build a prompt for one supported task kind and active wordlist."""
    spec = resolve_wordlist_spec(wordlist)
    try:
        instruction_template, label, deliverable = _PROMPT_SPECS[kind]
    except KeyError as exc:
        raise ValueError(f"Unsupported prompt kind: {kind}") from exc

    prompt = instruction_template.format(name=spec.name)
    if thinking:
        prompt += f" First write a short plan. Then give the final {deliverable}."

    words = ", ".join(spec.allowed_words())
    return f"{prompt}\n\nAllowed words ({spec.name}): {words}\n\n{label}: {content}\n"


__all__ = ["build_prompt"]
