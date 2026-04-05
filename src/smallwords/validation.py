"""Validate free-form text against the same vocabulary used elsewhere.

These helpers intentionally use a simple token-based view of text. They are
meant as a fast post-generation confidence check that stays aligned with the
wordlist surface forms, not as a full parser for every structural rule.
"""

from __future__ import annotations

import re

from ._spec_utils import resolve_wordlist_spec
from .types import WordlistSpec

# Keep tokenization deliberately simple so validation matches prompt wording.
WORD_RE = re.compile(r"[A-Za-z']+")


def normalize_tokens(text: str) -> list[str]:
    """Extract lowercase word tokens from free-form text.

    Args:
        text: Free-form text to tokenize.

    Returns:
        The lowercase word tokens found in the input text.
    """
    # The validator ignores punctuation so callers can check ordinary prose directly.
    return [token.lower() for token in WORD_RE.findall(text)]


def out_of_vocab(text: str, wordlist: str | WordlistSpec) -> list[str]:
    """Return sorted unique tokens that are missing from the selected word list.

    Args:
        text: Free-form text to validate.
        wordlist: Built-in wordlist name or inline wordlist specification.

    Returns:
        Sorted unique tokens that are not permitted by the selected wordlist.
    """
    spec = resolve_wordlist_spec(wordlist)
    # Membership checks happen against the normalized set so punctuation and
    # capitalization never create false negatives.
    allowed = set(spec.allowed_words())
    # A set comprehension keeps duplicates out of the report while staying deterministic.
    return sorted({token for token in normalize_tokens(text) if token not in allowed})


def is_compliant(text: str, wordlist: str | WordlistSpec) -> bool:
    """Return True when every normalized token is part of the selected word list.

    Args:
        text: Free-form text to validate.
        wordlist: Built-in wordlist name or inline wordlist specification.

    Returns:
        True when every normalized token is permitted by the selected wordlist.
    """
    # Compliance is intentionally defined in terms of vocabulary membership only.
    return not out_of_vocab(text, wordlist)
