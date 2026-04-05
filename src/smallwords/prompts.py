"""Provide prompt templates that stay aligned with the vocabulary constraints.

The package treats prompts as a soft steering layer rather than the only source
of truth. These helpers still matter because they tell a model which word list
is active and explicitly enumerate the allowed words, which often improves
results even before the grammar or schema starts constraining output.
"""

from __future__ import annotations

from ._spec_utils import resolve_wordlist_spec
from .types import WordlistSpec


def _resolve_spec(wordlist: str | WordlistSpec) -> WordlistSpec:
    """Normalize a prompt wordlist argument into a full specification.

    Args:
        wordlist: Built-in wordlist name or inline wordlist specification.

    Returns:
        The resolved wordlist specification object.
    """
    # Prompt helpers accept the same flexible inputs as the resource helpers.
    return resolve_wordlist_spec(wordlist)


def _allowed_words_block(wordlist: str | WordlistSpec) -> str:
    """Render the explicit vocabulary block the model should stay inside.

    Args:
        wordlist: Built-in wordlist name or inline wordlist specification.

    Returns:
        A prompt-ready line that lists every allowed word.
    """
    spec = _resolve_spec(wordlist)
    words = ", ".join(spec.allowed_words())
    # Spell out the available words so the prompt still helps without a grammar.
    return f"Allowed words ({spec.name}): {words}"


def prompt_explain_simply(
    topic: str, *, wordlist: str | WordlistSpec = "common_250", thinking: bool = False
) -> str:
    """Build an explanation prompt constrained to a named or inline word list.

    Args:
        topic: Topic the model should explain.
        wordlist: Built-in wordlist name or inline wordlist specification.
        thinking: Whether to ask for a visible planning step before the answer.

    Returns:
        A prompt string that includes both instructions and the allowed words.
    """
    spec = _resolve_spec(wordlist)
    # Keep the prompt text explicit about the wordlist name so it can be reused
    # even when the caller is not also passing a grammar or schema.
    prompt = (
        f"Explain the topic in plain English. Use only words from the {spec.name} word list. "
        "Use short sentences and concrete language."
    )
    if thinking:
        prompt += " First write a short plan. Then give the final answer."
    # The explicit vocabulary block helps both humans and models inspect the constraint.
    prompt += f"\n\n{_allowed_words_block(spec)}\n\nTopic: {topic}\n"
    return prompt


def prompt_summarize_simply(
    text: str, *, wordlist: str | WordlistSpec = "common_250", thinking: bool = False
) -> str:
    """Build a summarization prompt constrained to a named or inline word list.

    Args:
        text: Source text to summarize.
        wordlist: Built-in wordlist name or inline wordlist specification.
        thinking: Whether to ask for a visible planning step before the summary.

    Returns:
        A prompt string that includes both instructions and the allowed words.
    """
    spec = _resolve_spec(wordlist)
    prompt = (
        f"Summarize the text in plain English. Use only words from the {spec.name} word list. "
        "Keep the key points and cut extra detail."
    )
    if thinking:
        prompt += " First write a short plan. Then give the final summary."
    # Source text is separated from the vocabulary block so the prompt stays scannable.
    prompt += f"\n\n{_allowed_words_block(spec)}\n\nText:\n{text}\n"
    return prompt


def prompt_rewrite_simply(
    text: str, *, wordlist: str | WordlistSpec = "common_250", thinking: bool = False
) -> str:
    """Build a rewriting prompt constrained to a named or inline word list.

    Args:
        text: Source text to rewrite.
        wordlist: Built-in wordlist name or inline wordlist specification.
        thinking: Whether to ask for a visible planning step before the rewrite.

    Returns:
        A prompt string that includes both instructions and the allowed words.
    """
    spec = _resolve_spec(wordlist)
    prompt = (
        f"Rewrite the text in plain English. Use only words from the {spec.name} word list. "
        "Keep the meaning, but make the wording easier."
    )
    if thinking:
        prompt += " First write a short plan. Then give the final rewrite."
    # Rewriters need the original text preserved verbatim after the constraint block.
    prompt += f"\n\n{_allowed_words_block(spec)}\n\nText:\n{text}\n"
    return prompt


def prompt_answer_simply(
    question: str,
    *,
    wordlist: str | WordlistSpec = "common_250",
    thinking: bool = False,
) -> str:
    """Build a QA prompt constrained to a named or inline word list.

    Args:
        question: Question the model should answer.
        wordlist: Built-in wordlist name or inline wordlist specification.
        thinking: Whether to ask for a visible planning step before the answer.

    Returns:
        A prompt string that includes both instructions and the allowed words.
    """
    spec = _resolve_spec(wordlist)
    prompt = (
        f"Answer the question in plain English. Use only words from the {spec.name} word list. "
        "Be direct, brief, and clear."
    )
    if thinking:
        prompt += " First write a short plan. Then give the final answer."
    # Questions sit last so the active task is the freshest thing in the prompt.
    prompt += f"\n\n{_allowed_words_block(spec)}\n\nQuestion: {question}\n"
    return prompt


# Expose the templates as data so downstream code can build simple UIs on top.
TEMPLATE_PROMPTS = {
    "explain": prompt_explain_simply,
    "summarize": prompt_summarize_simply,
    "rewrite": prompt_rewrite_simply,
    "answer": prompt_answer_simply,
}
