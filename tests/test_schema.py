"""Tests for JSON Schema generation and alignment with the GBNF builder."""

import re

from smallwords import (
    BASIC_850,
    OutputResources,
    WordlistSpec,
    make_json_schema,
    make_resources,
)


def test_json_schema_is_single_key_and_strict() -> None:
    """Ensure default schemas stay strict and reject out-of-vocabulary text."""
    assert isinstance(BASIC_850, OutputResources)
    schema = BASIC_850.json_schema()

    assert schema["type"] == "object"
    assert schema["required"] == ["text"]
    assert schema["additionalProperties"] is False

    value_schema = schema["properties"]["text"]
    assert value_schema["type"] == "string"
    assert re.fullmatch(value_schema["pattern"], "The answer is clear.")
    assert re.fullmatch(value_schema["pattern"], "The boy made the bridge.")
    assert not re.fullmatch(value_schema["pattern"], "The neighbor can help.")


def test_json_schema_supports_custom_key_and_thinking_mode() -> None:
    """Ensure callers can customize both the key name and response wrapper."""
    schema = make_json_schema(
        "basic_850",
        key="answer",
        thinking_mode="plan_final",
        min_words_per_line=2,
        max_words_per_line=2,
        max_lines=1,
    )

    assert schema["required"] == ["answer"]
    assert re.fullmatch(
        schema["properties"]["answer"]["pattern"],
        "PLAN:\nwhy now.\n\nFINAL:\nanswer now.",
    )


def test_inline_constraints_stay_aligned_between_gbnf_and_schema() -> None:
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

    resources = make_resources(
        spec,
        min_words_per_line=2,
        max_words_per_line=2,
        max_lines=3,
    )
    schema = make_json_schema(
        spec,
        min_words_per_line=2,
        max_words_per_line=2,
        max_lines=3,
    )
    pattern = schema["properties"]["text"]["pattern"]

    # This test guards the shared constraint logic rather than either builder alone.
    assert "text ::= line" in resources.gbnf
    assert "line-prefix" not in resources.gbnf
    assert "punct ::=" not in resources.gbnf
    assert re.fullmatch(pattern, "one two")
    assert schema["properties"]["text"]["minLength"] == len("one two")
    assert not re.fullmatch(pattern, "one")
    assert not re.fullmatch(pattern, "- one")
    assert not re.fullmatch(pattern, "one\ntwo")
    assert not re.fullmatch(pattern, "one.")


def test_allow_numbers_are_supported_in_both_builders() -> None:
    """Ensure numeric tokens propagate through both constraint builders."""
    spec = WordlistSpec(name="count", words=("one",), allow_numbers=True)
    resources = make_resources(spec, max_words_per_line=1, max_lines=1)
    schema = make_json_schema(spec, max_words_per_line=1, max_lines=1)

    assert "number ::= [0-9]+" in resources.gbnf
    assert re.fullmatch(schema["properties"]["text"]["pattern"], "123")


def test_schema_can_match_generated_family_variants() -> None:
    """Ensure regex schemas accept expanded word-family variants."""
    spec = WordlistSpec(name="places", words=("city",))
    schema = make_json_schema(spec, max_words_per_line=1, max_lines=1)

    assert re.fullmatch(schema["properties"]["text"]["pattern"], "cities")
