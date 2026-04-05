"""Helpers for extending a base wordlist with words from a task prompt."""

from __future__ import annotations

from .remix import remix_wordlist
from .types import WordlistSpec
from .validation import normalize_tokens
from .wordlists import get_wordlist


def allow_input_words(
    wordlist: str | WordlistSpec,
    *texts: str,
    name: str | None = None,
    description: str | None = None,
) -> WordlistSpec:
    """Return a derived spec that also permits normalized words from task text."""
    base = get_wordlist(wordlist) if isinstance(wordlist, str) else wordlist
    allowed = set(base.allowed_words())
    extra_words: list[str] = []

    for text in texts:
        for token in normalize_tokens(text):
            # Only add genuinely new words so the derived spec stays tidy.
            if token not in allowed and token not in extra_words:
                extra_words.append(token)

    if not extra_words:
        return base

    return remix_wordlist(
        base,
        # Keep the base name by default so prompt text stays familiar.
        name=name or base.name,
        description=description
        or f"{base.description} Extended with normalized words from task input.",
        add_words=tuple(extra_words),
        source_name=f"{base.source_name} with task-input additions",
        source_urls=base.source_urls,
        license_name=base.license_name,
    )
