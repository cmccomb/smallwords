"""Prompt templates that mirror the package's controlled-language modes."""

from __future__ import annotations

from .types import WordlistSpec
from .wordlists import get_wordlist


def _resolve_spec(wordlist: str | WordlistSpec) -> WordlistSpec:
    """Normalize a wordlist argument into the full spec used by prompt builders."""
    return get_wordlist(wordlist) if isinstance(wordlist, str) else wordlist


def _allowed_words_block(wordlist: str | WordlistSpec) -> str:
    """Render the explicit vocabulary block the model should stay inside."""
    spec = _resolve_spec(wordlist)
    words = ", ".join(spec.allowed_words())
    # Spell out the available words so the prompt still helps without a grammar.
    return f"Allowed words ({spec.name}): {words}"


def prompt_explain_simply(
    topic: str, *, wordlist: str | WordlistSpec = "common_250", thinking: bool = False
) -> str:
    """Build an explanation prompt constrained to a named or inline word list."""
    spec = _resolve_spec(wordlist)
    # Keep the prompt text explicit about the wordlist name so it can be reused
    # even when the caller is not also passing a grammar or schema.
    prompt = (
        f"Explain the topic in plain English. Use only words from the {spec.name} word list. "
        "Use short sentences and concrete language."
    )
    if thinking:
        prompt += " First write a short plan. Then give the final answer."
    prompt += f"\n\n{_allowed_words_block(spec)}\n\nTopic: {topic}\n"
    return prompt


def prompt_summarize_simply(
    text: str, *, wordlist: str | WordlistSpec = "common_250", thinking: bool = False
) -> str:
    """Build a summarization prompt constrained to a named or inline word list."""
    spec = _resolve_spec(wordlist)
    prompt = (
        f"Summarize the text in plain English. Use only words from the {spec.name} word list. "
        "Keep the key points and cut extra detail."
    )
    if thinking:
        prompt += " First write a short plan. Then give the final summary."
    prompt += f"\n\n{_allowed_words_block(spec)}\n\nText:\n{text}\n"
    return prompt


def prompt_rewrite_simply(
    text: str, *, wordlist: str | WordlistSpec = "common_250", thinking: bool = False
) -> str:
    """Build a rewriting prompt constrained to a named or inline word list."""
    spec = _resolve_spec(wordlist)
    prompt = (
        f"Rewrite the text in plain English. Use only words from the {spec.name} word list. "
        "Keep the meaning, but make the wording easier."
    )
    if thinking:
        prompt += " First write a short plan. Then give the final rewrite."
    prompt += f"\n\n{_allowed_words_block(spec)}\n\nText:\n{text}\n"
    return prompt


def prompt_answer_simply(
    question: str,
    *,
    wordlist: str | WordlistSpec = "common_250",
    thinking: bool = False,
) -> str:
    """Build a QA prompt constrained to a named or inline word list."""
    spec = _resolve_spec(wordlist)
    prompt = (
        f"Answer the question in plain English. Use only words from the {spec.name} word list. "
        "Be direct, brief, and clear."
    )
    if thinking:
        prompt += " First write a short plan. Then give the final answer."
    prompt += f"\n\n{_allowed_words_block(spec)}\n\nQuestion: {question}\n"
    return prompt


# Expose the templates as data so downstream code can build simple UIs on top.
TEMPLATE_PROMPTS = {
    "explain": prompt_explain_simply,
    "summarize": prompt_summarize_simply,
    "rewrite": prompt_rewrite_simply,
    "answer": prompt_answer_simply,
}
