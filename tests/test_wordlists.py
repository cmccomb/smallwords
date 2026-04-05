"""Tests for the bundled source-backed wordlist catalog and presets."""

import pytest

from smallwords import (
    BASIC_850,
    CAVEMAN_898,
    MOBY_898,
    PIRATE_898,
    SPECIAL_ENGLISH_1475,
    get_wordlist,
    list_wordlists,
)


def test_documented_wordlists_are_available() -> None:
    """Ensure the bundled catalog exposes the documented built-in names."""
    assert {
        "moby_898",
        "basic_850",
        "special_english_1475",
        "caveman_898",
        "pirate_898",
    } == set(list_wordlists())


def test_wordlist_provenance_and_sizes() -> None:
    """Ensure the bundled wordlists carry provenance metadata and expected sizes."""
    moby = get_wordlist("moby_898")
    basic = get_wordlist("basic_850")
    special = get_wordlist("special_english_1475")

    # Provenance metadata is part of the public contract for bundled lists now.
    assert len(moby.words) == 898
    assert moby.source_name.startswith("Project Gutenberg Moby Words II")
    assert len(moby.source_urls) == 1
    assert moby.license_name == "Public domain"

    assert len(basic.words) == 850
    assert basic.source_name.startswith("Basic English 850")
    assert basic.license_name == "MIT"

    assert len(special.words) == 1475
    assert special.source_name.startswith("Voice of America Special English")
    assert special.license_name == "MIT"


def test_prebuilt_resource_presets_match_their_names() -> None:
    """Ensure exported resource presets line up with their documented wordlists."""
    assert BASIC_850.spec.name == "basic_850"
    assert MOBY_898.spec.name == "moby_898"
    assert CAVEMAN_898.spec.name == "caveman_898"
    assert PIRATE_898.spec.name == "pirate_898"
    assert SPECIAL_ENGLISH_1475.spec.name == "special_english_1475"


def test_themed_wordlists_are_size_neutral_moby_remixes() -> None:
    """Ensure the themed presets stay size-neutral relative to the Moby base."""
    moby = get_wordlist("moby_898")
    caveman = get_wordlist("caveman_898")
    pirate = get_wordlist("pirate_898")

    assert len(caveman.words) == len(moby.words) == 898
    assert len(pirate.words) == len(moby.words) == 898
    assert caveman.variant_mode == "surface_only"
    assert "ugh" in caveman.words
    assert "without" not in caveman.words
    assert "matey" in pirate.words
    assert pirate.variant_mode == "english_inflections"
    assert "authority" not in pirate.words


def test_default_family_expansion_stays_conservative() -> None:
    """Ensure built-in inflections add useful forms without obvious junk plurals."""
    moby = get_wordlist("moby_898")
    allowed = set(moby.allowed_words())

    assert "goes" in allowed
    assert "cities" in allowed
    assert "abouts" not in allowed
    assert "alwayses" not in allowed


def test_removed_wordlists_are_not_available() -> None:
    """Ensure the catalog no longer exposes ultra-short or format-mixed presets."""
    for name in (
        "common_50",
        "common_100",
        "common_250",
        "reasoning_250",
        "special_english",
        "caveman_250",
        "pirate_250",
    ):
        with pytest.raises(KeyError):
            get_wordlist(name)
