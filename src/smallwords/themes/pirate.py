"""Define the bundled pirate-themed remix.

This module keeps the themed adjustments intentionally compact so the pirate
vocabulary is easy to audit. Pirate mode is designed as a size-neutral remix:
it makes equal-sized additions and deletions while preserving the base
word-count and ordinary English inflection behavior.
"""

from __future__ import annotations

from ..remix import remix_wordlist
from ..types import WordlistSpec

# These additions give the pirate remix its playful nautical vocabulary.
PIRATE_EXTRA_WORDS = (
    "ahoy",
    "anchor",
    "aye",
    "crew",
    "deck",
    "harbor",
    "matey",
    "parrot",
    "plunder",
    "rum",
    "sail",
    "sea",
    "shore",
    "booty",
)

# These deletions balance the pirate additions so the remix stays size-neutral.
PIRATE_SWAP_OUT_WORDS = (
    "authority",
    "publish",
    "settle",
    "marriage",
    "fiscal",
    "interact",
    "democratic",
    "generally",
    "select",
    "importance",
    "march",
    "forget",
    "bank",
    "finish",
)


def build_pirate_spec(base: WordlistSpec) -> WordlistSpec:
    """Build a size-neutral pirate remix from a base vocabulary.

    Args:
        base: Base wordlist specification to remix.

    Returns:
        A derived pirate-flavored wordlist specification.
    """
    base_canonical = set(base.canonical_words())
    additions = tuple(word for word in PIRATE_EXTRA_WORDS if word not in base_canonical)
    removals = tuple(word for word in PIRATE_SWAP_OUT_WORDS if word in base_canonical)
    if len(additions) != len(removals):
        raise ValueError(
            "pirate remix must keep equal effective additions and deletions"
        )

    # Pirate mode keeps inflections so the speech stays lively instead of clipped.
    return remix_wordlist(
        base,
        name=f"pirate_{len(base.words)}",
        description="A size-neutral base-vocabulary remix with pirate-style adjustments for playful outputs.",
        add_words=additions,
        remove_words=removals,
        source_name=f"Derived from the bundled {base.name} wordlist with size-neutral pirate-style adjustments",
    )
