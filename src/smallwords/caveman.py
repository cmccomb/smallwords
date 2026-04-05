"""Caveman-flavored derived wordlist presets."""

from __future__ import annotations

from .remix import remix_wordlist
from .types import WordlistSpec

# These additions give the caveman remix a small themed vocabulary bump.
CAVEMAN_EXTRA_WORDS = (
    "big",
    "bone",
    "club",
    "fire",
    "food",
    "hunt",
    "rock",
    "strong",
    "tribe",
    "ugh",
)

# These drops remove helper words so the remix sounds clipped and telegraphic.
CAVEMAN_DROP_WORDS = (
    "a",
    "all",
    "also",
    "and",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "have",
    "if",
    "in",
    "it",
    "of",
    "on",
    "or",
    "so",
    "than",
    "that",
    "the",
    "there",
    "these",
    "they",
    "this",
    "through",
    "to",
    "we",
    "which",
    "with",
)


def build_caveman_spec(base: WordlistSpec) -> WordlistSpec:
    """Remix a base wordlist into a clipped, telegraphic caveman variant.

    Args:
        base: Base wordlist specification to remix.

    Returns:
        A derived caveman-flavored wordlist specification.
    """
    # Surface-only forms keep the output choppy and intentionally less polished.
    return remix_wordlist(
        base,
        name="caveman_250",
        description="A clipped base-vocabulary remix with caveman-style extras and fewer helper words.",
        add_words=CAVEMAN_EXTRA_WORDS,
        remove_words=CAVEMAN_DROP_WORDS,
        source_name="Derived from the bundled common_250 wordlist with caveman-style additions/removals",
        variant_mode="surface_only",
        blocked_forms=("goes", "going", "made", "running"),
    )
