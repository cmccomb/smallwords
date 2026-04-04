from __future__ import annotations

import re
from typing import Iterable

from .types import WordlistSpec
from .wordlists import get_wordlist

WORD_RE = re.compile(r"[A-Za-z']+")


def normalize_tokens(text: str) -> list[str]:
    return [token.lower() for token in WORD_RE.findall(text)]



def out_of_vocab(text: str, wordlist: str | WordlistSpec) -> list[str]:
    spec = get_wordlist(wordlist) if isinstance(wordlist, str) else wordlist
    allowed = set(spec.normalized_words())
    return sorted({token for token in normalize_tokens(text) if token not in allowed})



def is_compliant(text: str, wordlist: str | WordlistSpec) -> bool:
    return not out_of_vocab(text, wordlist)
