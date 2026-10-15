"""Define the bundled storybook-pirate vocabulary remix."""

from __future__ import annotations

from ..remix import remix_wordlist
from ..types import WordlistSpec
from ._shared import ABSTRACT_SWAP_OUT_WORDS, SPOKEN_EXTRA_WORDS

# A practical mix of greetings, people, places, gear, and actions. The preset is
# playful rather than a claim about how historical pirates actually spoke.
PIRATE_EXTRA_WORDS = (
    "ahoy",
    "anchor",
    "aye",
    "booty",
    "cannon",
    "compass",
    "crew",
    "deck",
    "flag",
    "gold",
    "harbor",
    "island",
    "loot",
    "map",
    "mast",
    "matey",
    "mutiny",
    "parrot",
    "pirate",
    "plank",
    "plunder",
    "port",
    "rope",
    "rum",
    "sail",
    "sailor",
    "sea",
    "shore",
    "storm",
    "treasure",
    "voyage",
)

PIRATE_SWAP_OUT_WORDS = ABSTRACT_SWAP_OUT_WORDS


def build_pirate_spec(base: WordlistSpec) -> WordlistSpec:
    """Build a size-neutral pirate remix with useful spoken words.

    Args:
        base: Base wordlist specification to remix.

    Returns:
        A derived pirate-flavored wordlist specification.
    """
    base_canonical = set(base.canonical_words())
    additions = tuple(
        word
        for word in (*SPOKEN_EXTRA_WORDS, *PIRATE_EXTRA_WORDS)
        if word not in base_canonical
    )
    removals = tuple(word for word in PIRATE_SWAP_OUT_WORDS if word in base_canonical)
    if len(additions) != len(removals):
        raise ValueError(
            "pirate remix must keep equal effective additions and deletions"
        )

    return remix_wordlist(
        base,
        name=f"pirate_{len(base.words)}",
        description="A size-neutral Moby remix for clear, playful pirate stories and greetings.",
        add_words=additions,
        remove_words=removals,
        source_name=f"Derived from {base.name} with curated storybook pirate terms",
        source_urls=tuple(
            dict.fromkeys(
                (
                    *base.source_urls,
                    "https://www.rmg.co.uk/press-release/international-talk-pirate-weekend",
                )
            )
        ),
        style_hint=(
            "Use a playful pirate voice when it fits the task. "
            "Choose ship and sea words naturally, and keep the meaning clear."
        ),
    )
