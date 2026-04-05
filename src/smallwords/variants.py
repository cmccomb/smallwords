"""Expand canonical vocabularies into conservative surface-form families."""

from __future__ import annotations

from collections.abc import Iterable
from functools import lru_cache

from ._variant_data import (
    AUTO_NOUN_BASES,
    AUTO_VERB_BASES,
    DOUBLE_FINAL_CONSONANT_VERBS,
    IRREGULAR_FAMILIES,
    IRREGULAR_NOUNS,
    NON_INFLECTING_WORDS,
)
from .types import WordFamily, WordlistSpec


def _normalize(words: Iterable[str]) -> tuple[str, ...]:
    """Lowercase, trim, and sort words for deterministic output resources."""
    return tuple(sorted({word.strip().lower() for word in words if word.strip()}))


def _plural_like(word: str) -> str:
    """Build a conservative plural or third-person-singular form."""
    if word.endswith(("s", "sh", "ch", "x", "z", "o")):
        return word + "es"
    if len(word) > 1 and word.endswith("y") and word[-2] not in "aeiou":
        return word[:-1] + "ies"
    return word + "s"


def _gerund(word: str) -> str:
    """Build a regular English ``-ing`` form without broad doubling heuristics."""
    if word in DOUBLE_FINAL_CONSONANT_VERBS:
        return word + word[-1] + "ing"
    if len(word) > 2 and word.endswith("ie"):
        return word[:-2] + "ying"
    if len(word) > 2 and word.endswith("e") and not word.endswith(("ee", "ye")):
        return word[:-1] + "ing"
    return word + "ing"


def _past(word: str) -> str:
    """Build a regular English past-tense or participle form."""
    if word in DOUBLE_FINAL_CONSONANT_VERBS:
        return word + word[-1] + "ed"
    if len(word) > 1 and word.endswith("y") and word[-2] not in "aeiou":
        return word[:-1] + "ied"
    if word.endswith("e"):
        return word + "d"
    return word + "ed"


def _regular_noun_forms(word: str) -> set[str]:
    """Generate safe noun-style variants for a canonical headword."""
    if word in NON_INFLECTING_WORDS or len(word) < 2:
        return set()
    return {_plural_like(word)}


def _regular_verb_forms(word: str) -> set[str]:
    """Generate regular verb variants for curated base verbs only."""
    return {_plural_like(word), _gerund(word), _past(word)}


def _family_forms(family: WordFamily) -> set[str]:
    """Expand one explicit family annotation into allowed surface forms."""
    word = family.headword.strip().lower()
    forms = {word, *(form.strip().lower() for form in family.forms if form.strip())}

    if family.kind == "noun":
        forms.update(_regular_noun_forms(word))
    elif family.kind == "verb":
        forms.update(_regular_verb_forms(word))

    return forms


def _auto_forms(word: str, *, variant_mode: str) -> set[str]:
    """Generate built-in English family forms for one canonical word."""
    if variant_mode != "english_inflections":
        return {word}

    forms = {word}
    if word in IRREGULAR_FAMILIES:
        forms.update(IRREGULAR_FAMILIES[word])
    elif word in AUTO_VERB_BASES:
        forms.update(_regular_verb_forms(word))

    if word in IRREGULAR_NOUNS:
        forms.update(IRREGULAR_NOUNS[word])
    elif word in AUTO_NOUN_BASES:
        forms.update(_regular_noun_forms(word))

    return forms


@lru_cache(maxsize=128)
def canonical_words(spec: WordlistSpec) -> tuple[str, ...]:
    """Return the normalized canonical words for a wordlist spec."""
    return _normalize(spec.words)


@lru_cache(maxsize=128)
def expand_allowed_words(spec: WordlistSpec) -> tuple[str, ...]:
    """Expand a spec's canonical words into the surface forms callers may emit."""
    families = {
        family.headword.strip().lower(): family for family in spec.word_families
    }
    blocked = {word.strip().lower() for word in spec.blocked_forms if word.strip()}

    allowed: set[str] = set()
    for word in canonical_words(spec):
        allowed.update(_auto_forms(word, variant_mode=spec.variant_mode))
        if word in families:
            allowed.update(_family_forms(families[word]))

    for family in families.values():
        allowed.update(_family_forms(family))

    allowed.difference_update(blocked)
    return _normalize(allowed)
