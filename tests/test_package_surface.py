"""Tests for the small, public package surface expected by PyPI users."""

from smallwords import __version__, list_wordlists


def test_package_exposes_installed_version() -> None:
    """Ensure the package root exposes a usable installed version string."""
    # The exact value can vary for source-tree imports, but it should always be present.
    assert isinstance(__version__, str)
    assert __version__


def test_wordlist_catalog_is_not_empty() -> None:
    """Ensure the package root exposes at least one bundled wordlist name."""
    assert list_wordlists()
