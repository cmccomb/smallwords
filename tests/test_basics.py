"""Behavior tests for the main constrained-text workflow."""

from smallwords import (
    OutputResources,
    OutputShape,
    WordFamily,
    WordlistSpec,
    allow_input_words,
    is_compliant,
    out_of_vocab,
)
from smallwords.prompts import build_prompt


def test_build_prompt_mentions_wordlist_and_task_text() -> None:
    """Ensure the prompt text names the selected wordlist and lists allowed words."""
    prompt = build_prompt("explain", "How does rain work?", wordlist="basic_850")
    assert "basic_850" in prompt
    assert "Allowed words (basic_850):" in prompt
    assert "goes" in prompt
    assert "Topic: How does rain work?" in prompt


def test_allow_input_words_adds_question_terms() -> None:
    """Ensure task words can be added to the allowed vocabulary on demand."""
    spec = allow_input_words("basic_850", "How can a neighbor help?")
    prompt = build_prompt("explain", "How can a neighbor help?", wordlist=spec)
    assert "neighbor" in prompt
    assert is_compliant("A neighbor can help.", spec)


def test_output_resources_from_wordlist_exposes_gbnf_root() -> None:
    """Ensure resource bundles expose a top-level GBNF root rule."""
    resources = OutputResources.from_wordlist("basic_850")
    assert resources.gbnf.startswith("root ::= text")


def test_validation_distinguishes_compliant_and_out_of_vocab_text() -> None:
    """Ensure compliant and out-of-vocabulary text are distinguished."""
    assert is_compliant("The answer is clear.", "basic_850")
    assert "neighbor" in out_of_vocab("The neighbor can help.", "basic_850")


def test_inflected_variants_are_allowed_by_default() -> None:
    """Ensure built-ins accept family variants like ``goes`` and ``made``."""
    assert is_compliant("He goes out.", "basic_850")
    assert is_compliant("The boy made the bridge.", "basic_850")


def test_surface_only_mode_stays_literal() -> None:
    """Ensure surface-only specs reject variants that were not listed directly."""
    spec = WordlistSpec(name="tiny", words=("go",), variant_mode="surface_only")
    assert is_compliant("go", spec)
    assert not is_compliant("goes", spec)


def test_explicit_word_family_can_extend_custom_specs() -> None:
    """Ensure inline specs can add irregular or verb-style families explicitly."""
    spec = WordlistSpec(
        name="tiny_try",
        words=("try",),
        word_families=(WordFamily("try", kind="verb"),),
    )
    assert is_compliant("tries tried trying", spec)


def test_resources_reuse_inline_shapes() -> None:
    """Ensure resource bundles preserve the selected output shape."""
    shape = OutputShape(min_words_per_line=2, max_words_per_line=9, max_lines=3)
    spec = allow_input_words("basic_850", "How can a neighbor help?")
    resources = OutputResources.from_wordlist(spec, shape=shape)
    assert resources.shape == shape
    assert "text ::= line (newline line){0,2}" in resources.gbnf
