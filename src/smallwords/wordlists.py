"""Bundle the built-in vocabularies shipped with the library.

This module is the catalog for every supported built-in wordlist. It loads the
raw text resources, publishes the direct source-backed vocabularies, and derives
the themed presets that the rest of the package treats as canonical built-ins.
"""

from __future__ import annotations

from importlib.resources import files

from .themes import build_caveman_spec, build_pirate_spec
from .types import WordlistSpec

# This resource root holds the bundled wordlist text files shipped with the package.
_DATA_ROOT = files("smallwords").joinpath("data")


def _load_bundled_words(filename: str) -> tuple[str, ...]:
    """Load a normalized one-word-per-line resource file from the package.

    Args:
        filename: Resource filename inside the bundled data directory.

    Returns:
        The normalized words found in the resource file.
    """
    words: list[str] = []
    # The resource format stays intentionally simple so bundled data is easy to audit.
    for raw_line in (
        _DATA_ROOT.joinpath(filename).read_text(encoding="utf-8").splitlines()
    ):
        line = raw_line.strip().lower()
        if not line or line.startswith("#"):
            continue
        words.append(line)
    return tuple(words)


# This frequency-ranked source list anchors the bundled Moby vocabulary.
MOBY_FREQ_WORDS = _load_bundled_words("moby_freq_alpha_898.txt")
# This bundled list provides the permissive Basic English preset.
BASIC_850_WORDS = _load_bundled_words("basic_english_850.txt")
# This bundled list provides the Special English preset.
SPECIAL_ENGLISH_WORDS = _load_bundled_words("special_english_1475.txt")

# This bundled spec exposes the full normalized Moby frequency list.
MOBY_898_SPEC = WordlistSpec(
    name="moby_898",
    words=MOBY_FREQ_WORDS,
    description="The full normalized alpha-only Moby Words II frequency list bundled with the package.",
    source_name="Project Gutenberg Moby Words II freq.txt normalized to alpha-only tokens",
    source_urls=(
        "https://www.gutenberg.org/files/3201/files/freq.txt",
    ),
    license_name="Public domain",
)

# This bundled spec exposes the Basic English preset.
BASIC_850_SPEC = WordlistSpec(
    name="basic_850",
    words=BASIC_850_WORDS,
    description="Charles Ogden's Basic English 850, bundled as a normalized built-in list.",
    source_name="Basic English 850 via the J. Burkardt dataset mirror",
    source_urls=(
        "https://people.sc.fsu.edu/~jburkardt/datasets/words/basic_english_850.txt",
    ),
    license_name="MIT",
)

# This bundled spec exposes the Special English preset.
SPECIAL_ENGLISH_1475_SPEC = WordlistSpec(
    name="special_english_1475",
    words=SPECIAL_ENGLISH_WORDS,
    description="Voice of America Special English, bundled as a normalized built-in list.",
    source_name="Voice of America Special English via the J. Burkardt dataset mirror",
    source_urls=(
        "https://people.sc.fsu.edu/~jburkardt/datasets/words/special_english.txt",
    ),
    license_name="MIT",
)

# This bundled spec exposes the caveman remix preset.
CAVEMAN_898_SPEC = build_caveman_spec(MOBY_898_SPEC)
# This bundled spec exposes the pirate remix preset.
PIRATE_898_SPEC = build_pirate_spec(MOBY_898_SPEC)

# This catalog maps every bundled wordlist name to its specification.
WORDLISTS: dict[str, WordlistSpec] = {
    MOBY_898_SPEC.name: MOBY_898_SPEC,
    BASIC_850_SPEC.name: BASIC_850_SPEC,
    SPECIAL_ENGLISH_1475_SPEC.name: SPECIAL_ENGLISH_1475_SPEC,
    CAVEMAN_898_SPEC.name: CAVEMAN_898_SPEC,
    PIRATE_898_SPEC.name: PIRATE_898_SPEC,
}


def get_wordlist(name: str) -> WordlistSpec:
    """Return a named bundled wordlist or raise a helpful KeyError.

    Args:
        name: Built-in wordlist name.

    Returns:
        The matching bundled wordlist specification.

    Raises:
        KeyError: If the requested name is not registered.
    """
    try:
        return WORDLISTS[name]
    except KeyError as exc:
        # Include the available names to make prompt-time mistakes easy to correct.
        raise KeyError(
            f"Unknown wordlist: {name!r}. Available: {sorted(WORDLISTS)}"
        ) from exc


def list_wordlists() -> tuple[str, ...]:
    """Return the bundled wordlist names in stable sorted order.

    Returns:
        The available bundled wordlist names.
    """
    # Sorting keeps docs, tests, and UI pickers deterministic.
    return tuple(sorted(WORDLISTS))
