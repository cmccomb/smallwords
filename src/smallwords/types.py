from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class WordlistSpec:
    """Configuration for a controlled-vocabulary word list."""

    name: str
    words: tuple[str, ...]
    description: str = ""
    allow_capitalized_words: bool = True
    allow_numbers: bool = False
    allow_newlines: bool = True
    allowed_punctuation: tuple[str, ...] = (".", ",", "!", "?", ":", ";")
    line_prefixes: tuple[str, ...] = field(default_factory=tuple)

    def normalized_words(self) -> tuple[str, ...]:
        return tuple(sorted({w.strip().lower() for w in self.words if w.strip()}))
