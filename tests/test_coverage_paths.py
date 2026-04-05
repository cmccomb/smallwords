"""Target branchy coverage paths that matter for runtime behavior."""

from __future__ import annotations

import importlib
import importlib.metadata
import re

import pytest

import smallwords
from smallwords.grammar_builder import build_gbnf
from smallwords.json_schema import (
    _max_response_length,
    _max_text_length,
    _pattern_alt,
    _response_pattern,
    _word_pattern,
    build_json_schema,
)
from smallwords.types import WordFamily, WordlistSpec
from smallwords.wordlists import get_wordlist


def test_package_version_falls_back_when_metadata_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure source-tree imports keep a safe fallback version string."""

    def _raise_package_not_found(_: str) -> str:
        """Raise the same error the import path handles during reload."""
        raise importlib.metadata.PackageNotFoundError

    monkeypatch.setattr(importlib.metadata, "version", _raise_package_not_found)
    reloaded = importlib.reload(smallwords)
    try:
        assert reloaded.__version__ == "0+unknown"
    finally:
        # Reload again after undoing the patch so later tests see the normal module state.
        monkeypatch.undo()
        importlib.reload(reloaded)


def test_build_gbnf_supports_prefixes_numbers_and_thinking_wrappers() -> None:
    """Ensure the grammar builder emits optional advanced rules when requested."""
    spec = WordlistSpec(
        name="bullet_count",
        words=("go",),
        allow_capitalized_words=False,
        allow_numbers=True,
        line_prefixes=("- ", "1. "),
    )

    grammar = build_gbnf(
        spec,
        thinking_mode="thinking_answer",
        max_words_per_line=2,
        max_lines=2,
    )
    plan_grammar = build_gbnf(
        spec,
        thinking_mode="plan_final",
        max_words_per_line=2,
        max_lines=2,
    )

    assert 'root ::= "THINKING:' in grammar
    assert 'root ::= "PLAN:' in plan_grammar
    assert "number ::= [0-9]+" in grammar
    assert 'line-prefix ::= "- " | "1. "' in grammar
    assert "line ::= line-prefix? word (space word){0,1} punct?" in grammar


def test_build_gbnf_rejects_invalid_settings() -> None:
    """Ensure the grammar builder fails fast on invalid limits and modes."""
    spec = WordlistSpec(name="tiny", words=("go",), variant_mode="surface_only")

    with pytest.raises(ValueError, match="max_words_per_line must be >= 1"):
        build_gbnf(spec, max_words_per_line=0)
    with pytest.raises(ValueError, match="max_lines must be >= 1"):
        build_gbnf(spec, max_lines=0)
    with pytest.raises(ValueError, match="Wordlist must contain at least one word"):
        build_gbnf(WordlistSpec(name="empty", words=()), max_words_per_line=1)
    with pytest.raises(ValueError, match="Unsupported thinking_mode"):
        build_gbnf(spec, thinking_mode="mystery")  # type: ignore[arg-type]


def test_json_schema_helpers_cover_singletons_and_error_paths() -> None:
    """Ensure the regex helpers handle edge cases and validation failures."""
    spec = WordlistSpec(name="tiny", words=("go",), allow_capitalized_words=False)

    assert _pattern_alt(["go"]) == "go"
    with pytest.raises(ValueError, match="Wordlist must contain at least one word"):
        _word_pattern(WordlistSpec(name="empty", words=()))
    with pytest.raises(ValueError, match="Wordlist must contain at least one word"):
        _max_text_length(
            WordlistSpec(name="empty", words=()), max_words_per_line=1, max_lines=1
        )
    with pytest.raises(ValueError, match="key must be a non-empty string"):
        build_json_schema(spec, key="")
    with pytest.raises(ValueError, match="max_words_per_line must be >= 1"):
        build_json_schema(spec, max_words_per_line=0)
    with pytest.raises(ValueError, match="max_lines must be >= 1"):
        build_json_schema(spec, max_lines=0)


def test_json_schema_supports_thinking_answer_and_rejects_bad_modes() -> None:
    """Ensure schema helpers mirror both wrapper modes and mode validation."""
    spec = WordlistSpec(
        name="tiny",
        words=("go",),
        allow_capitalized_words=False,
        allow_newlines=False,
        allowed_punctuation=(),
        variant_mode="surface_only",
    )

    schema = build_json_schema(
        spec,
        thinking_mode="thinking_answer",
        max_words_per_line=1,
        max_lines=1,
    )
    pattern = schema["properties"]["text"]["pattern"]

    assert re.fullmatch(pattern, "THINKING:\ngo\n\nANSWER:\ngo")
    assert _max_response_length(
        spec,
        thinking_mode="thinking_answer",
        max_words_per_line=1,
        max_lines=1,
    ) == len("THINKING:\ngo\n\nANSWER:\ngo")
    with pytest.raises(ValueError, match="Unsupported thinking_mode"):
        _response_pattern(
            spec,
            thinking_mode="mystery",  # type: ignore[arg-type]
            max_words_per_line=1,
            max_lines=1,
        )
    with pytest.raises(ValueError, match="Unsupported thinking_mode"):
        _max_response_length(
            spec,
            thinking_mode="mystery",  # type: ignore[arg-type]
            max_words_per_line=1,
            max_lines=1,
        )


def test_explicit_word_families_cover_regular_inflection_edges() -> None:
    """Ensure family metadata can drive conservative regular edge inflections."""
    spec = WordlistSpec(
        name="families",
        words=(),
        variant_mode="surface_only",
        word_families=(
            WordFamily("stop", kind="verb"),
            WordFamily("die", kind="verb"),
            WordFamily("a", kind="noun"),
            WordFamily("city", kind="noun"),
        ),
    )
    allowed = set(spec.allowed_words())

    assert {"stop", "stopped", "stopping"} <= allowed
    assert {"die", "dying"} <= allowed
    assert {"city", "cities"} <= allowed
    assert "as" not in allowed


def test_unknown_wordlist_error_lists_available_names() -> None:
    """Ensure lookup errors point users toward the valid built-in names."""
    with pytest.raises(KeyError, match="Available"):
        get_wordlist("definitely_not_real")
