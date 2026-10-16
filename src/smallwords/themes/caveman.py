"""Build the short, chiefly Germanic-rooted caveman vocabulary."""

from __future__ import annotations

from importlib.resources import files

from ..remix import remix_wordlist
from ..types import WordlistSpec


def build_caveman_spec(base: WordlistSpec) -> WordlistSpec:
    """Keep curated one-syllable words, including a few useful exceptions."""
    resource = files("smallwords").joinpath(
        "data", "caveman_germanic_monosyllables.txt"
    )
    curated = {
        line.strip()
        for line in resource.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }
    base_words = set(base.canonical_words())

    # Retain the existing public name: 898 identifies the source list, not the
    # smaller vocabulary produced by this stricter filter.
    return remix_wordlist(
        base,
        name=f"caveman_{len(base.words)}",
        description="A curated set of one-syllable, chiefly Germanic-rooted words for a blunt caveman voice.",
        add_words=tuple(sorted(curated - base_words)),
        remove_words=tuple(sorted(base_words - curated)),
        source_name=f"Curated from the bundled {base.name} list using pronunciation and etymology checks",
        source_urls=base.source_urls
        + (
            "https://github.com/cmusphinx/cmudict",
            "https://github.com/cavedave/EnglishWords",
            "https://en.wiktionary.org/wiki/Help:Etymology",
        ),
        variant_mode="surface_only",
        style_hint="Use short, blunt sentences with simple, concrete words.",
    )
