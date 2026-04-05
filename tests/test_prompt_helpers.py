"""Tests for prompt helpers and resource-writing convenience methods."""

from __future__ import annotations

import json
from pathlib import Path

from smallwords import (
    OutputResources,
    WordlistSpec,
    allow_input_words,
    get_wordlist,
    make_resources,
    prompt_answer_simply,
    prompt_explain_simply,
    prompt_rewrite_simply,
    prompt_summarize_simply,
)
from smallwords.prompts import TEMPLATE_PROMPTS


def test_prompt_builders_include_constraints_and_task_text() -> None:
    """Ensure every prompt helper includes the active vocabulary and task text."""
    spec = WordlistSpec(name="tiny", words=("go",), variant_mode="surface_only")
    prompts = {
        "explain": prompt_explain_simply("Why go?", wordlist=spec, thinking=True),
        "summarize": prompt_summarize_simply("Go now.", wordlist=spec, thinking=True),
        "rewrite": prompt_rewrite_simply("Go now.", wordlist=spec, thinking=True),
        "answer": prompt_answer_simply("Why go?", wordlist=spec, thinking=True),
    }

    # Every helper should surface the same explicit word block and plan hint.
    for prompt in prompts.values():
        assert "Allowed words (tiny): go" in prompt
        assert "First write a short plan." in prompt

    assert "Topic: Why go?" in prompts["explain"]
    assert "Text:\nGo now.\n" in prompts["summarize"]
    assert "Text:\nGo now.\n" in prompts["rewrite"]
    assert "Question: Why go?" in prompts["answer"]


def test_template_prompt_catalog_points_at_public_helpers() -> None:
    """Ensure the exported template catalog stays aligned with the public API."""
    assert TEMPLATE_PROMPTS["explain"] is prompt_explain_simply
    assert TEMPLATE_PROMPTS["summarize"] is prompt_summarize_simply
    assert TEMPLATE_PROMPTS["rewrite"] is prompt_rewrite_simply
    assert TEMPLATE_PROMPTS["answer"] is prompt_answer_simply


def test_allow_input_words_reuses_base_spec_when_no_words_are_added() -> None:
    """Ensure task-word expansion returns the original spec when nothing changes."""
    base = get_wordlist("common_50")
    derived = allow_input_words(base, "The man can make it.")

    assert derived is base


def test_resource_helpers_write_gbnf_and_schema_files(tmp_path: Path) -> None:
    """Ensure portable resources can be saved to disk for downstream runtimes."""
    resources = make_resources("common_50", max_words_per_line=2, max_lines=1)
    assert isinstance(resources, OutputResources)

    gbnf_path = tmp_path / "tiny.gbnf"
    schema_path = tmp_path / "tiny.json"

    resources.save_gbnf(str(gbnf_path))
    resources.save_json_schema(
        str(schema_path),
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


def test_normalized_words_matches_allowed_words() -> None:
    """Ensure the compatibility alias still returns the expanded surface forms."""
    spec = WordlistSpec(name="tiny", words=(" Go ", "go"), variant_mode="surface_only")

    assert spec.normalized_words() == spec.allowed_words() == ("go",)
