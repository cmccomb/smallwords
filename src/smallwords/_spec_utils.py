"""Keep wordlist resolution logic in one small internal place.

Several public helpers accept either a bundled wordlist name or an inline
``WordlistSpec`` object. Centralizing that coercion here keeps the behavior
consistent and gives future maintainers one place to change if resolution rules
ever grow more complex.
"""

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
    # A tiny shared helper avoids subtle drift between prompt/resource/validation code.
    return get_wordlist(wordlist) if isinstance(wordlist, str) else wordlist
