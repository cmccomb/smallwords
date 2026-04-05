"""Core shared data structures used by the package."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class WordlistSpec:
    """Configuration for a controlled-vocabulary word list."""

    name: str
    words: tuple[str, ...]
    description: str = ""
    source_name: str = ""
    source_urls: tuple[str, ...] = field(default_factory=tuple)
    license_name: str = ""
    allow_capitalized_words: bool = True
    allow_numbers: bool = False
    allow_newlines: bool = True
    allowed_punctuation: tuple[str, ...] = (".", ",", "!", "?", ":", ";")
    line_prefixes: tuple[str, ...] = field(default_factory=tuple)

    def normalized_words(self) -> tuple[str, ...]:
        """Return de-duplicated lowercase words sorted for stable grammar output."""
        return tuple(sorted({w.strip().lower() for w in self.words if w.strip()}))
