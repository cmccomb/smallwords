"""Validation helpers for checking text against a controlled vocabulary."""

from __future__ import annotations

import re

from .types import WordlistSpec
from .wordlists import get_wordlist

# Keep tokenization deliberately simple so validation matches prompt wording.
WORD_RE = re.compile(r"[A-Za-z']+")


def normalize_tokens(text: str) -> list[str]:
    """Extract lowercase word tokens from free-form text."""
    return [token.lower() for token in WORD_RE.findall(text)]


def out_of_vocab(text: str, wordlist: str | WordlistSpec) -> list[str]:
    """Return sorted unique tokens that are missing from the selected word list."""
    spec = get_wordlist(wordlist) if isinstance(wordlist, str) else wordlist
    # Membership checks happen against the normalized set so punctuation and
    # capitalization never create false negatives.
    allowed = set(spec.normalized_words())
    return sorted({token for token in normalize_tokens(text) if token not in allowed})


def is_compliant(text: str, wordlist: str | WordlistSpec) -> bool:
    """Return True when every normalized token is part of the selected word list."""
    return not out_of_vocab(text, wordlist)
