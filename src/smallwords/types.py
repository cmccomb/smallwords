"""Define the shared vocabulary data structures used across the package.

These types intentionally stay lightweight because they are threaded through the
prompt builders, grammar generation, schema generation, and validation layers.
Keeping the model simple makes it easier for both humans and tools to trace how
a controlled vocabulary flows through the system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# Variant modes describe how far the package should expand a canonical headword.
VariantMode = Literal["surface_only", "english_inflections"]
# Family kinds let callers opt into explicit noun- or verb-style behavior.
FamilyKind = Literal["custom", "noun", "verb"]


@dataclass(frozen=True)
class WordFamily:
    """Explicit word-family metadata for irregular or hand-tuned variants.

    Attributes:
        headword: Canonical word that anchors the family.
        kind: Family expansion behavior to apply around the headword.
        forms: Extra literal forms that should always be allowed.
    """

    headword: str
    kind: FamilyKind = "custom"
    forms: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class WordlistSpec:
    """Configuration for a controlled-vocabulary word list.

    Attributes:
        name: Human-readable and programmatic name for the vocabulary.
        words: Canonical words that define provenance for the vocabulary.
        description: Short description of the vocabulary's purpose.
        source_name: Human-readable provenance label for the vocabulary source.
        source_urls: Source URLs that document where the vocabulary came from.
        license_name: License label for the bundled or derived vocabulary.
        allow_capitalized_words: Whether capitalized word variants are accepted.
        allow_numbers: Whether numeric tokens are accepted alongside words.
        allow_newlines: Whether outputs may span multiple lines.
        allowed_punctuation: Punctuation marks allowed at the end of a line.
        line_prefixes: Optional allowed bullet or numbering prefixes per line.
        variant_mode: Automatic expansion mode for inflected surface forms.
        word_families: Explicit families that supplement automatic expansion.
        blocked_forms: Surface forms that should be excluded after expansion.
    """

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
        # Canonical words are the provenance source of truth for the wordlist.
        return tuple(sorted({w.strip().lower() for w in self.words if w.strip()}))

    def allowed_words(self) -> tuple[str, ...]:
        """Return the expanded set of allowed surface forms for this spec.

        Returns:
            The allowed surface forms after applying the variant policy.
        """
        # Expansion is delegated so every caller shares the same family logic.
        from .variants import expand_allowed_words

        return expand_allowed_words(self)

    def normalized_words(self) -> tuple[str, ...]:
        """Return normalized allowed words for backward compatibility.

        Returns:
            The normalized allowed words used by older call sites.
        """
        # Historically callers used `normalized_words()` for the grammar surface.
        return self.allowed_words()
