"""Tests for the bundled source-backed wordlist catalog and presets."""

from smallwords import (
    COMMON_50_THINKING,
    COMMON_100_THINKING,
    COMMON_250_THINKING,
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
    assert REASONING_250.spec.name == "reasoning_250"
