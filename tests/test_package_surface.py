"""Tests for the intentionally small root package surface."""

from __future__ import annotations

import importlib

import pytest

import smallwords
from smallwords.prompts import build_prompt


def test_package_exposes_expected_root_api() -> None:
    """Ensure the root namespace stays small and predictable."""
    for name in (
        "OutputResources",
        "OutputShape",
        "WordFamily",
        "WordlistSpec",
        "allow_input_words",
        "get_wordlist",
        "is_compliant",
        "list_wordlists",
        "out_of_vocab",
        "remix_wordlist",
    ):
        assert hasattr(smallwords, name)

    for name in (
        "make_resources",
        "make_gbnf",
        "make_json_schema",
        "prompt_answer_simply",
        "prompt_explain_simply",
        "prompt_rewrite_simply",
        "prompt_summarize_simply",
        "BASIC_850",
        "MOBY_898",
        "PIRATE_898",
        "CAVEMAN_898",
        "SPECIAL_ENGLISH_1475",
        "build_prompt",
    ):
        assert not hasattr(smallwords, name)


def test_package_exposes_installed_version() -> None:
    """Ensure the package root exposes a usable installed version string."""
    assert isinstance(smallwords.__version__, str)
    assert smallwords.__version__


def test_build_prompt_stays_public_via_prompts_module() -> None:
    """Ensure the consolidated prompt entrypoint stays module-scoped."""
    assert callable(build_prompt)


def test_integrations_package_is_removed() -> None:
    """Ensure runtime-specific helpers no longer ship as library API."""
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("smallwords.integrations")
