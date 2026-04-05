"""Core shared data structures used by the package."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

VariantMode = Literal["surface_only", "english_inflections"]
FamilyKind = Literal["custom", "noun", "verb"]


@dataclass(frozen=True)
class WordFamily:
    """Explicit word-family metadata for irregular or hand-tuned variants."""

    headword: str
    kind: FamilyKind = "custom"
    forms: tuple[str, ...] = field(default_factory=tuple)


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
    variant_mode: VariantMode = "english_inflections"
    word_families: tuple[WordFamily, ...] = field(default_factory=tuple)
    blocked_forms: tuple[str, ...] = field(default_factory=tuple)

    def canonical_words(self) -> tuple[str, ...]:
        """Return the normalized canonical word list as authored in the spec.

        Returns:
            The canonical words from the specification in normalized sort order.
        """
        # Stable ordering keeps generated grammars and schemas reproducible.
        return tuple(sorted({w.strip().lower() for w in self.words if w.strip()}))

    def allowed_words(self) -> tuple[str, ...]:
        """Return the expanded set of allowed surface forms for this spec.

        Returns:
            The allowed surface forms after applying the variant policy.
        """
        from .variants import expand_allowed_words

        return expand_allowed_words(self)

    def normalized_words(self) -> tuple[str, ...]:
        """Return normalized allowed words for backward compatibility.

        Returns:
            The normalized allowed words used by older call sites.
        """
        # Historically callers used `normalized_words()` for the grammar surface.
        return self.allowed_words()
