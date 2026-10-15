"""Define the bundled cowboy and ranch-hand vocabulary remix."""

from __future__ import annotations

from ..remix import remix_wordlist
from ..types import WordlistSpec
from ._shared import ABSTRACT_SWAP_OUT_WORDS, SPOKEN_EXTRA_WORDS

# These words cover ranch work, horses, the trail, and a few familiar greetings.
# Terms such as vaquero, lariat, and chaps also reflect the trade's origins.
COWBOY_EXTRA_WORDS = (
    "barn",
    "boot",
    "bronco",
    "buckaroo",
    "calf",
    "camp",
    "cattle",
    "chaps",
    "corral",
    "cow",
    "cowboy",
    "dust",
    "hat",
    "herd",
    "howdy",
    "lariat",
    "lasso",
    "longhorn",
    "prairie",
    "ranch",
    "rein",
    "rodeo",
    "rope",
    "roundup",
    "saddle",
    "spur",
    "steer",
    "trail",
    "vaquero",
    "wagon",
    "wrangler",
)

COWBOY_SWAP_OUT_WORDS = ABSTRACT_SWAP_OUT_WORDS


def build_cowboy_spec(base: WordlistSpec) -> WordlistSpec:
    """Build a size-neutral cowboy remix with useful spoken words.

    Args:
        base: Base wordlist specification to remix.

    Returns:
        A derived cowboy-flavored wordlist specification.
    """
    base_canonical = set(base.canonical_words())
    additions = tuple(
        word
        for word in (*SPOKEN_EXTRA_WORDS, *COWBOY_EXTRA_WORDS)
        if word not in base_canonical
    )
    removals = tuple(word for word in COWBOY_SWAP_OUT_WORDS if word in base_canonical)
    if len(additions) != len(removals):
        raise ValueError(
            "cowboy remix must keep equal effective additions and deletions"
        )

    return remix_wordlist(
        base,
        name=f"cowboy_{len(base.words)}",
        description="A size-neutral Moby remix for clear cowboy and ranch stories.",
        add_words=additions,
        remove_words=removals,
        source_name=f"Derived from {base.name} with curated cowboy and vaquero terms",
        source_urls=tuple(
            dict.fromkeys(
                (
                    *base.source_urls,
                    "https://www.nps.gov/tapr/learn/historyculture/cowboys.htm",
                    "https://www.nps.gov/articles/000/rancho.htm",
                )
            )
        ),
        style_hint=(
            "Use a warm ranch-hand voice when it fits the task. "
            "Choose horse, cattle, and trail words naturally, and keep the meaning clear."
        ),
    )
