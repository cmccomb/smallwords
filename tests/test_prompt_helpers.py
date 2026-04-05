"""Tests for the prompt builder and resource-writing convenience methods."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from smallwords import OutputResources, OutputShape, WordlistSpec, allow_input_words
from smallwords.prompts import build_prompt


def test_build_prompt_supports_all_task_kinds_and_thinking() -> None:
    """Ensure every prompt kind includes the active vocabulary and task text."""
    spec = WordlistSpec(name="tiny", words=("go",), variant_mode="surface_only")
    prompts = {
        "explain": build_prompt("explain", "Why go?", wordlist=spec, thinking=True),
        "summarize": build_prompt("summarize", "Go now.", wordlist=spec, thinking=True),
        "rewrite": build_prompt("rewrite", "Go now.", wordlist=spec, thinking=True),
        "answer": build_prompt("answer", "Why go?", wordlist=spec, thinking=True),
    }

    for prompt in prompts.values():
        assert "Allowed words (tiny): go" in prompt
        assert "First write a short plan." in prompt

    assert "Topic: Why go?" in prompts["explain"]
    assert "Text: Go now." in prompts["summarize"]
    assert "Text: Go now." in prompts["rewrite"]
    assert "Question: Why go?" in prompts["answer"]


def test_build_prompt_rejects_unknown_kind() -> None:
    """Ensure unsupported prompt kinds fail with a helpful error."""
    with pytest.raises(ValueError, match="Unsupported prompt kind"):
        build_prompt("unknown", "hello")  # type: ignore[arg-type]


def test_allow_input_words_reuses_base_spec_when_no_words_are_added() -> None:
    """Ensure task-word expansion returns the original spec when nothing changes."""
    base = WordlistSpec(name="tiny", words=("the", "answer", "is", "clear"))
    derived = allow_input_words(base, "The answer is clear.")
    assert derived is base


def test_resource_helpers_write_gbnf_and_schema_files(tmp_path: Path) -> None:
    """Ensure portable resources can be saved to disk for downstream runtimes."""
    shape = OutputShape(max_words_per_line=2, max_lines=1)
    resources = OutputResources.from_wordlist("basic_850", shape=shape)

    gbnf_path = tmp_path / "tiny.gbnf"
    schema_path = tmp_path / "tiny.json"

    resources.save_gbnf(gbnf_path)
    resources.save_json_schema(
        schema_path,
        key="answer",
        title="Tiny response",
        description="Short answer.",
    )

    with open(gbnf_path, encoding="utf-8") as handle:
        assert handle.read() == resources.gbnf

    with open(schema_path, encoding="utf-8") as handle:
        saved_schema = json.load(handle)

    assert saved_schema["title"] == "Tiny response"
    assert saved_schema["properties"]["answer"]["description"] == "Short answer."
