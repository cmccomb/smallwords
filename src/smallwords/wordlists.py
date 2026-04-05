"""Bundled source-backed word lists and lookup helpers."""

from __future__ import annotations

from importlib.resources import files

from .types import WordlistSpec

_DATA_ROOT = files("smallwords").joinpath("data")


def _load_bundled_words(filename: str) -> tuple[str, ...]:
    """Load a normalized one-word-per-line resource file from the package."""
    words: list[str] = []
    for raw_line in (
        _DATA_ROOT.joinpath(filename).read_text(encoding="utf-8").splitlines()
    ):
        line = raw_line.strip().lower()
        if not line or line.startswith("#"):
            continue
        words.append(line)
    return tuple(words)


MOBY_FREQ_WORDS = _load_bundled_words("moby_freq_alpha_898.txt")
BASIC_850_WORDS = _load_bundled_words("basic_english_850.txt")
SPECIAL_ENGLISH_WORDS = _load_bundled_words("special_english_1477.txt")

# The short `common_*` tiers keep the broad frequency ordering from Moby while
# filtering through Special English so the built-ins stay simple and general.
SPECIAL_ENGLISH_SET = set(SPECIAL_ENGLISH_WORDS)
COMMON_SOURCE_WORDS = tuple(
    word for word in MOBY_FREQ_WORDS if word in SPECIAL_ENGLISH_SET
)

COMMON_50_WORDS = COMMON_SOURCE_WORDS[:50]
COMMON_100_WORDS = COMMON_SOURCE_WORDS[:100]
COMMON_250_WORDS = COMMON_SOURCE_WORDS[:250]

REASONING_SUPPLEMENT = (
    "answer",
    "check",
    "clear",
    "final",
    "list",
    "next",
    "note",
    "plan",
    "result",
    "step",
    "steps",
    "story",
    "why",
)

SIMPLE_REASONING_WORDS = tuple(dict.fromkeys(COMMON_250_WORDS + REASONING_SUPPLEMENT))

COMMON_50_SPEC = WordlistSpec(
    name="common_50",
    words=COMMON_50_WORDS,
    description="Fifty high-frequency words ranked by Moby frequency and filtered to Special English.",
    source_name="Project Gutenberg Moby Words II filtered through VOA Special English",
    source_urls=(
        "https://www.gutenberg.org/files/3201/files/freq.txt",
        "https://people.sc.fsu.edu/~jburkardt/datasets/words/special_english.txt",
    ),
    license_name="Public domain + MIT",
)

COMMON_100_SPEC = WordlistSpec(
    name="common_100",
    words=COMMON_100_WORDS,
    description="One hundred high-frequency words ranked by Moby frequency and filtered to Special English.",
    source_name="Project Gutenberg Moby Words II filtered through VOA Special English",
    source_urls=(
        "https://www.gutenberg.org/files/3201/files/freq.txt",
        "https://people.sc.fsu.edu/~jburkardt/datasets/words/special_english.txt",
    ),
    license_name="Public domain + MIT",
)

COMMON_250_SPEC = WordlistSpec(
    name="common_250",
    words=COMMON_250_WORDS,
    description="Two hundred fifty high-frequency words ranked by Moby frequency and filtered to Special English.",
    source_name="Project Gutenberg Moby Words II filtered through VOA Special English",
    source_urls=(
        "https://www.gutenberg.org/files/3201/files/freq.txt",
        "https://people.sc.fsu.edu/~jburkardt/datasets/words/special_english.txt",
    ),
    license_name="Public domain + MIT",
)

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

SPECIAL_ENGLISH_SPEC = WordlistSpec(
    name="special_english",
    words=SPECIAL_ENGLISH_WORDS,
    description="Voice of America Special English, bundled as a normalized built-in list.",
    source_name="Voice of America Special English via the J. Burkardt dataset mirror",
    source_urls=(
        "https://people.sc.fsu.edu/~jburkardt/datasets/words/special_english.txt",
    ),
    license_name="MIT",
)

REASONING_250_SPEC = WordlistSpec(
    name="reasoning_250",
    words=SIMPLE_REASONING_WORDS,
    description="`common_250` plus a small authored planning supplement for visible reasoning blocks.",
    source_name="Derived from the bundled common_250 wordlist with authored planning additions",
    source_urls=COMMON_250_SPEC.source_urls,
    license_name="Public domain + MIT",
    line_prefixes=("- ", "1. ", "2. ", "3. "),
)

WORDLISTS: dict[str, WordlistSpec] = {
    COMMON_50_SPEC.name: COMMON_50_SPEC,
    COMMON_100_SPEC.name: COMMON_100_SPEC,
    COMMON_250_SPEC.name: COMMON_250_SPEC,
    BASIC_850_SPEC.name: BASIC_850_SPEC,
    SPECIAL_ENGLISH_SPEC.name: SPECIAL_ENGLISH_SPEC,
    REASONING_250_SPEC.name: REASONING_250_SPEC,
}


def get_wordlist(name: str) -> WordlistSpec:
    """Return a named bundled wordlist or raise a helpful KeyError."""
    try:
        return WORDLISTS[name]
    except KeyError as exc:
        raise KeyError(
            f"Unknown wordlist: {name!r}. Available: {sorted(WORDLISTS)}"
        ) from exc
