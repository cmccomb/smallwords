"""Let callers re-introduce task words without broadening the whole package.

This module is the opt-in escape hatch for prompts like ``bridge`` or
``neighbor`` that may not live in a compact base vocabulary. The helper returns
a regular ``WordlistSpec`` so the rest of the package can treat the expanded
spec exactly like any other vocabulary.
"""

from __future__ import annotations

from ._spec_utils import resolve_wordlist_spec
from .remix import remix_wordlist
from .types import WordlistSpec
from .validation import normalize_tokens


def allow_input_words(
    wordlist: str | WordlistSpec,
    *texts: str,
    name: str | None = None,
    description: str | None = None,
) -> WordlistSpec:
    """Return a derived spec that also permits normalized words from task text.

    Args:
        wordlist: Built-in wordlist name or inline wordlist specification.
        texts: One or more task strings whose normalized words should be allowed.
        name: Optional replacement name for the derived specification.
        description: Optional replacement description for the derived specification.

    Returns:
        A derived wordlist specification that includes the task words.
    """
    base = resolve_wordlist_spec(wordlist)
    # Compare against the already-expanded surface forms so we do not add needless duplicates.
    allowed = set(base.allowed_words())
    extra_words: list[str] = []

    for text in texts:
        for token in normalize_tokens(text):
            # Only add genuinely new words so the derived spec stays tidy.
            if token not in allowed and token not in extra_words:
                extra_words.append(token)

    if not extra_words:
        # Reuse the original object when nothing new needs to be allowed.
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
