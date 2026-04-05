"""Helpers for deriving playful or task-specific wordlists from a base vocab."""

from __future__ import annotations

from .types import VariantMode, WordlistSpec


def remix_wordlist(
    base: WordlistSpec,
    *,
    name: str,
    description: str,
    add_words: tuple[str, ...] = (),
    remove_words: tuple[str, ...] = (),
    source_name: str | None = None,
    source_urls: tuple[str, ...] | None = None,
    license_name: str | None = None,
    variant_mode: VariantMode | None = None,
    line_prefixes: tuple[str, ...] | None = None,
    blocked_forms: tuple[str, ...] = (),
) -> WordlistSpec:
    """Build a derived wordlist from a base list plus curated additions/removals."""
    canonical = set(base.canonical_words())
    canonical.update(word.strip().lower() for word in add_words if word.strip())
    canonical.difference_update(
        word.strip().lower() for word in remove_words if word.strip()
    )

    # Derived presets inherit the base constraints unless the caller overrides them.
    return WordlistSpec(
        name=name,
        words=tuple(sorted(canonical)),
        description=description,
        source_name=source_name
        or f"{base.source_name} with curated additions/removals",
        source_urls=source_urls or base.source_urls,
        license_name=license_name or base.license_name,
        allow_capitalized_words=base.allow_capitalized_words,
        allow_numbers=base.allow_numbers,
        allow_newlines=base.allow_newlines,
        allowed_punctuation=base.allowed_punctuation,
        line_prefixes=line_prefixes
        if line_prefixes is not None
        else base.line_prefixes,
        variant_mode=variant_mode or base.variant_mode,
        word_families=base.word_families,
        blocked_forms=tuple(dict.fromkeys(base.blocked_forms + blocked_forms)),
    )
