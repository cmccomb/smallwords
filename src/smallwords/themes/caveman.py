"""Define the bundled caveman-themed remix.

This module stays intentionally small and discoverable so future maintainers
can see exactly how the caveman preset differs from its base vocabulary.
Caveman mode is designed as a size-neutral remix: it makes equal-sized
additions and deletions while also tightening inflection behavior. Long words
are swapped for short, concrete words.
"""

from __future__ import annotations

from ..remix import remix_wordlist
from ..types import WordlistSpec

# These additions give the caveman remix its rougher themed vocabulary.
CAVEMAN_EXTRA_WORDS = (
    "bone",
    "cave",
    "grub",
    "hunt",
    "meat",
    "rock",
    "smash",
    "spear",
    "stone",
    "ugh",
)

# These deletions balance the caveman additions so the remix stays size-neutral.
CAVEMAN_SWAP_OUT_WORDS = (
    "about",
    "among",
    "between",
    "during",
    "however",
    "include",
    "only",
    "several",
    "toward",
    "without",
)

# Short, concrete replacements for base words with ten or more letters.
CAVEMAN_SHORT_REPLACEMENT_WORDS = (
    "ash",
    "axe",
    "bark",
    "bat",
    "bee",
    "bug",
    "cat",
    "claw",
    "cow",
    "cub",
    "den",
    "dirt",
    "duck",
    "egg",
    "fish",
    "fox",
    "frog",
    "fur",
    "goat",
    "hen",
    "hut",
    "ice",
    "leaf",
    "log",
    "milk",
    "moon",
    "mud",
    "nest",
    "nut",
    "owl",
    "pig",
    "rain",
    "rope",
    "smoke",
    "snow",
    "sun",
    "tent",
    "wolf",
    "wood",
)


def build_caveman_spec(base: WordlistSpec) -> WordlistSpec:
    """Build a size-neutral caveman remix from a base vocabulary.

    Args:
        base: Base wordlist specification to remix.

    Returns:
        A derived caveman-flavored wordlist specification.
    """
    base_canonical = set(base.canonical_words())
    additions = tuple(
        word
        for word in CAVEMAN_EXTRA_WORDS + CAVEMAN_SHORT_REPLACEMENT_WORDS
        if word not in base_canonical
    )
    long_base_words = tuple(word for word in base.canonical_words() if len(word) >= 10)
    removals = tuple(
        dict.fromkeys(
            word
            for word in CAVEMAN_SWAP_OUT_WORDS + long_base_words
            if word in base_canonical
        )
    )
    if len(additions) != len(removals):
        raise ValueError(
            "caveman remix must keep equal effective additions and deletions"
        )

    # Surface-only forms keep the output choppy and intentionally less polished.
    # A few blocked inflections keep the voice from drifting back toward ordinary prose.
    return remix_wordlist(
        base,
        name=f"caveman_{len(base.words)}",
        description="A size-neutral base-vocabulary remix with short, concrete words and rougher surface forms.",
        add_words=additions,
        remove_words=removals,
        source_name=f"Derived from the bundled {base.name} wordlist with size-neutral caveman-style adjustments",
        variant_mode="surface_only",
        blocked_forms=("goes", "going", "made", "running"),
    )
