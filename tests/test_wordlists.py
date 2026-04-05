"""Tests for the bundled source-backed wordlist catalog and presets."""

from smallwords import (
    CAVEMAN_250,
    COMMON_50_THINKING,
    COMMON_100_THINKING,
    COMMON_250_THINKING,
    PIRATE_250,
    REASONING_250,
    WORDLISTS,
    get_wordlist,
)


def test_source_backed_wordlists_are_available() -> None:
    """Ensure the bundled catalog exposes the documented built-in names."""
    assert {
        "common_50",
        "common_100",
        "common_250",
        "basic_850",
        "special_english",
        "reasoning_250",
        "caveman_250",
        "pirate_250",
    } <= WORDLISTS.keys()


def test_wordlist_provenance_and_sizes() -> None:
    """Ensure the bundled wordlists carry provenance metadata and expected sizes."""
    common = get_wordlist("common_250")
    basic = get_wordlist("basic_850")
    special = get_wordlist("special_english")

    # Provenance metadata is part of the public contract for bundled lists now.
    assert len(common.words) == 250
    assert common.source_name.startswith("Project Gutenberg Moby Words II")
    assert len(common.source_urls) == 2
    assert common.license_name == "Public domain + MIT"

    assert len(basic.words) == 850
    assert basic.source_name.startswith("Basic English 850")
    assert basic.license_name == "MIT"

    assert len(special.words) == 1475
    assert special.source_name.startswith("Voice of America Special English")
    assert special.license_name == "MIT"


def test_prebuilt_resource_presets_match_their_names() -> None:
    """Ensure exported resource presets line up with their documented wordlists."""
    # The thinking presets should keep their named base vocabularies.
    assert COMMON_50_THINKING.spec.name == "common_50"
    assert COMMON_100_THINKING.spec.name == "common_100"
    assert COMMON_250_THINKING.spec.name == "common_250"
    assert CAVEMAN_250.spec.name == "caveman_250"
    assert PIRATE_250.spec.name == "pirate_250"
    assert REASONING_250.spec.name == "reasoning_250"


def test_themed_wordlists_remix_the_base_vocab() -> None:
    """Ensure the easter-egg presets are derived from the base vocabulary."""
    caveman = get_wordlist("caveman_250")
    pirate = get_wordlist("pirate_250")

    assert caveman.variant_mode == "surface_only"
    assert "ugh" in caveman.words
    assert "the" not in caveman.words
    assert "matey" in pirate.words
    assert pirate.variant_mode == "english_inflections"


def test_default_family_expansion_stays_conservative() -> None:
    """Ensure built-in inflections add useful forms without obvious junk plurals."""
    common = get_wordlist("common_250")
    allowed = set(common.allowed_words())

    assert "goes" in allowed
    assert "cities" in allowed
    assert "abouts" not in allowed
    assert "alwayses" not in allowed
