"""Define the public data structures used across the package."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# Variant modes describe how far the package should expand a canonical headword.
VariantMode = Literal["surface_only", "english_inflections"]
# Family kinds let callers opt into explicit noun- or verb-style behavior.
FamilyKind = Literal["custom", "noun", "verb"]
# Thinking modes describe whether a response includes an explicit planning block.
ThinkingMode = Literal["none", "plan_final", "thinking_answer"]


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
class OutputShape:
    """Describe the serialized response shape shared by every output resource.

    Attributes:
        thinking_mode: Wrapper mode for plain text or plan/final style responses.
        min_words_per_line: Minimum number of tokens required on one line.
        max_words_per_line: Maximum number of tokens allowed on one line.
        max_lines: Maximum number of lines allowed in the response body.
    """

    thinking_mode: ThinkingMode = "none"
    min_words_per_line: int = 1
    max_words_per_line: int = 40
    max_lines: int = 8

    def __post_init__(self) -> None:
        """Reject invalid output limits as soon as a shape is constructed."""
        from ._constraints import validate_output_shape

        validate_output_shape(self)


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
        from .variants import canonical_words

        return canonical_words(self)

    def allowed_words(self) -> tuple[str, ...]:
        """Return the expanded set of allowed surface forms for this spec.

        Returns:
            The allowed surface forms after applying the variant policy.
        """
        from .variants import expand_allowed_words

        return expand_allowed_words(self)
