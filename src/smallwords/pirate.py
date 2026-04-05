"""Pirate-flavored derived wordlist presets."""

from __future__ import annotations

from .remix import remix_wordlist
from .types import WordlistSpec

PIRATE_EXTRA_WORDS = (
    "ahoy",
    "anchor",
    "aye",
    "captain",
    "crew",
    "deck",
    "gold",
    "harbor",
    "matey",
    "rum",
    "sail",
    "sea",
    "ship",
    "shore",
)


def build_pirate_spec(base: WordlistSpec) -> WordlistSpec:
    """Remix a base wordlist into a pirate-flavored playful variant."""
    # Pirate mode keeps inflections so the speech stays lively instead of clipped.
    return remix_wordlist(
        base,
        name="pirate_250",
        description="A base-vocabulary remix with pirate-style extras for playful outputs.",
        add_words=PIRATE_EXTRA_WORDS,
        source_name="Derived from the bundled common_250 wordlist with pirate-style additions",
    )
