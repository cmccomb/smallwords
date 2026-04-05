"""Tests for shared constraint serialization through GBNF and JSON Schema."""

import re

import pytest

from smallwords import OutputResources, OutputShape, WordlistSpec


def test_output_shape_rejects_invalid_limits_and_modes() -> None:
    """Ensure invalid shape settings fail fast."""
    with pytest.raises(ValueError, match="min_words_per_line must be >= 1"):
        OutputShape(min_words_per_line=0)
    with pytest.raises(ValueError, match="max_words_per_line must be >= 1"):
        OutputShape(max_words_per_line=0)
    with pytest.raises(ValueError, match="min_words_per_line must be <= max_words_per_line"):
        OutputShape(min_words_per_line=2, max_words_per_line=1)
    with pytest.raises(ValueError, match="max_lines must be >= 1"):
        OutputShape(max_lines=0)
    with pytest.raises(ValueError, match="Unsupported thinking_mode"):
        OutputShape(thinking_mode="mystery")  # type: ignore[arg-type]


def test_json_schema_is_single_key_and_strict() -> None:
    """Ensure default schemas stay strict and reject out-of-vocabulary text."""
    resources = OutputResources.from_wordlist("basic_850")
    schema = resources.json_schema()

    assert schema["type"] == "object"
    assert schema["required"] == ["text"]
    assert schema["additionalProperties"] is False

    value_schema = schema["properties"]["text"]
    assert value_schema["type"] == "string"
    assert value_schema["minLength"] > 0
    assert re.fullmatch(value_schema["pattern"], "The answer is clear.")
    assert re.fullmatch(value_schema["pattern"], "The boy made the bridge.")
    assert not re.fullmatch(value_schema["pattern"], "The neighbor can help.")


def test_custom_shape_stays_aligned_between_gbnf_and_schema() -> None:
    """Ensure inline specs produce matching grammar and schema constraints."""
    spec = WordlistSpec(
        name="tiny",
        words=("one", "two"),
        allow_capitalized_words=False,
        allow_numbers=False,
        allow_newlines=False,
        allowed_punctuation=(),
        line_prefixes=(),
    )
    shape = OutputShape(min_words_per_line=2, max_words_per_line=2, max_lines=3)
    resources = OutputResources.from_wordlist(spec, shape=shape)
    schema = resources.json_schema()
    pattern = schema["properties"]["text"]["pattern"]

    assert "text ::= line" in resources.gbnf
    assert "line-prefix" not in resources.gbnf
    assert "punct ::=" not in resources.gbnf
    assert re.fullmatch(pattern, "one two")
    assert schema["properties"]["text"]["minLength"] == len("one two")
    assert schema["properties"]["text"]["maxLength"] == len("one two")
    assert not re.fullmatch(pattern, "one")
    assert not re.fullmatch(pattern, "- one")
    assert not re.fullmatch(pattern, "one\ntwo")
    assert not re.fullmatch(pattern, "one.")


def test_plan_final_shape_wraps_both_serializers() -> None:
    """Ensure thinking wrappers stay aligned across both formats."""
    spec = WordlistSpec(
        name="tiny",
        words=("why", "now", "answer"),
        allow_capitalized_words=False,
        allow_newlines=False,
        allowed_punctuation=(".",),
        variant_mode="surface_only",
    )
    shape = OutputShape(
        thinking_mode="plan_final",
        min_words_per_line=2,
        max_words_per_line=2,
        max_lines=1,
    )
    resources = OutputResources.from_wordlist(spec, shape=shape)
    schema = resources.json_schema(key="answer")

    assert 'root ::= "PLAN:" newline text newline newline "FINAL:" newline text' in resources.gbnf
    assert re.fullmatch(
        schema["properties"]["answer"]["pattern"],
        "PLAN:\nwhy now.\n\nFINAL:\nanswer now.",
    )


def test_prefixes_punctuation_and_numbers_are_supported() -> None:
    """Ensure optional prefix, punctuation, and number support flows through both serializers."""
    spec = WordlistSpec(
        name="count",
        words=("go",),
        allow_capitalized_words=False,
        allow_numbers=True,
        line_prefixes=("- ", "1. "),
    )
    shape = OutputShape(min_words_per_line=2, max_words_per_line=2, max_lines=2)
    resources = OutputResources.from_wordlist(spec, shape=shape)
    schema = resources.json_schema()

    assert "number ::= [0-9]+" in resources.gbnf
    assert 'line-prefix ::= "- " | "1. "' in resources.gbnf
    assert "line ::= line-prefix? word (space word){1,1} punct?" in resources.gbnf
    assert re.fullmatch(schema["properties"]["text"]["pattern"], "1. go 123.")


def test_number_only_specs_are_supported() -> None:
    """Ensure number-only specs serialize consistently across both formats."""
    spec = WordlistSpec(name="digits", words=(), allow_numbers=True)
    shape = OutputShape(max_words_per_line=1, max_lines=1)
    resources = OutputResources.from_wordlist(spec, shape=shape)
    schema = resources.json_schema()

    assert "number ::= [0-9]+" in resources.gbnf
    assert "common-word ::=" not in resources.gbnf
    assert re.fullmatch(schema["properties"]["text"]["pattern"], "123")
    assert "maxLength" not in schema["properties"]["text"]


def test_empty_wordlists_without_numbers_are_rejected() -> None:
    """Ensure empty vocabularies still fail with a helpful error."""
    resources = OutputResources.from_wordlist(WordlistSpec(name="empty", words=()))
    with pytest.raises(ValueError, match="Wordlist must contain at least one word"):
        _ = resources.gbnf
    with pytest.raises(ValueError, match="Wordlist must contain at least one word"):
        resources.json_schema()


def test_json_schema_rejects_empty_keys() -> None:
    """Ensure schema keys must stay non-empty."""
    resources = OutputResources.from_wordlist("basic_850")
    with pytest.raises(ValueError, match="key must be a non-empty string"):
        resources.json_schema(key="")
