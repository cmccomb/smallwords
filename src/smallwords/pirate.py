"""Define the bundled pirate-themed remix.

Like the caveman preset, this module stays intentionally compact so the themed
edits are easy to audit. Pirate mode keeps regular inflections enabled because
the goal is playful speech, not broken or ultra-telegraphic language.
"""

from __future__ import annotations

from .remix import remix_wordlist
from .types import WordlistSpec

# These additions give the pirate remix its playful nautical vocabulary.
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
    """Remix a base wordlist into a pirate-flavored playful variant.

    Args:
        base: Base wordlist specification to remix.

    Returns:
        A derived pirate-flavored wordlist specification.
    """
    # Pirate mode keeps inflections so the speech stays lively instead of clipped.
    # The remix only adds flavor words; it otherwise behaves like the base vocabulary.
    return remix_wordlist(
        base,
        name="pirate_250",
        description="A base-vocabulary remix with pirate-style extras for playful outputs.",
        add_words=PIRATE_EXTRA_WORDS,
        source_name="Derived from the bundled common_250 wordlist with pirate-style additions",
    )
