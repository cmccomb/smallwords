"""Tests for vocabulary-only checks and full output validation."""

from __future__ import annotations

import re

import pytest

from smallwords import (
    OutputResources,
    OutputShape,
    WordlistSpec,
    is_compliant,
    is_in_vocabulary,
    validate_output,
)


@pytest.fixture
def tiny_resources() -> OutputResources:
    """Create a small contract with easy-to-inspect valid responses."""
    spec = WordlistSpec(
        name="tiny",
        words=("go", "now"),
        allow_capitalized_words=False,
        allow_numbers=False,
        allow_newlines=False,
        allowed_punctuation=(".",),
        variant_mode="surface_only",
    )
    shape = OutputShape(min_words_per_line=2, max_words_per_line=2, max_lines=1)
    return OutputResources.from_wordlist(spec, shape=shape)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("go now.", True),
        ("", False),
        ("123", False),
        ("go $$$ now", False),
        ("Go now.", False),
        ("go now now.", False),
        ("go\nnow", False),
        ("go now?", False),
        ("go stop.", False),
    ],
)
def test_full_validation_agrees_with_schema_pattern(
    tiny_resources: OutputResources, text: str, expected: bool
) -> None:
    """Match the generated text pattern for valid and invalid responses."""
    result = tiny_resources.validate(text)
    pattern = tiny_resources.json_schema()["properties"]["text"]["pattern"]

    assert result.valid is expected
    assert (re.fullmatch(pattern, text, flags=re.ASCII) is not None) is expected
    assert bool(result.issues) is not expected
    assert (
        validate_output(text, tiny_resources.spec, shape=tiny_resources.shape) == result
    )


def test_validation_reports_out_of_vocabulary_words(
    tiny_resources: OutputResources,
) -> None:
    """Identify unfamiliar words in addition to rejecting the full response."""
    result = tiny_resources.validate("go stop.")
    assert result.out_of_vocab == ("stop",)
    assert result.issues[0] == "Out-of-vocabulary words: stop"


def test_wrapper_labels_are_not_reported_as_out_of_vocabulary() -> None:
    """Accept the labels used by the configured plan/final output shape."""
    spec = WordlistSpec(
        name="tiny",
        words=("go", "now", "wait"),
        variant_mode="surface_only",
    )
    shape = OutputShape(
        thinking_mode="plan_final",
        min_words_per_line=2,
        max_words_per_line=2,
        max_lines=1,
    )
    text = "PLAN:\ngo now.\n\nFINAL:\nwait now."
    result = validate_output(text, spec, shape=shape)

    assert result.valid
    assert result.out_of_vocab == ()
    assert result.issues == ()


def test_vocabulary_only_helpers_remain_compatible(
    tiny_resources: OutputResources,
) -> None:
    """Keep the prior behavior while offering a more precise helper name."""
    assert is_compliant("", tiny_resources.spec)
    assert is_in_vocabulary("", tiny_resources.spec)
    assert is_compliant("123", tiny_resources.spec)
    assert is_in_vocabulary("123", tiny_resources.spec)
    assert not is_compliant("go stop", tiny_resources.spec)
