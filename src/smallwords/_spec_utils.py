"""Internal helpers for working with named or inline wordlist specs."""

from __future__ import annotations

from .types import WordlistSpec
from .wordlists import get_wordlist


def resolve_wordlist_spec(wordlist: str | WordlistSpec) -> WordlistSpec:
    """Return a full spec object for a named or inline wordlist value.

    Args:
        wordlist: Built-in wordlist name or inline wordlist specification.

    Returns:
        The resolved wordlist specification object.
    """
    # Accepting both names and inline specs keeps the public API ergonomic.
    return get_wordlist(wordlist) if isinstance(wordlist, str) else wordlist
