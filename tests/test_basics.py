"""Basic smoke tests for prompts, grammars, and validation helpers."""

from smallwords import (
    BASIC_850,
    WordFamily,
    WordlistSpec,
    allow_input_words,
    is_compliant,
    make_gbnf,
    make_resources,
    out_of_vocab,
    prompt_explain_simply,
)


def test_prompt_mentions_wordlist() -> None:
    """Ensure the prompt text names the selected wordlist and lists allowed words."""
    prompt = prompt_explain_simply("How does rain work?", wordlist="basic_850")
    assert "basic_850" in prompt
    assert "Allowed words (basic_850):" in prompt
    assert "goes" in prompt


def test_allow_input_words_adds_question_terms() -> None:
    """Ensure task words can be added to the allowed vocabulary on demand."""
    spec = allow_input_words("basic_850", "How can a neighbor help?")
    prompt = prompt_explain_simply("How can a neighbor help?", wordlist=spec)
    assert "neighbor" in prompt
    assert is_compliant("A neighbor can help.", spec)


def test_gbnf_has_root() -> None:
    """Ensure prebuilt resources expose a top-level GBNF root rule."""
    assert BASIC_850.gbnf.startswith("root ::= text")


def test_make_gbnf_matches_resource_bundle() -> None:
    """Ensure the direct helper mirrors the resource bundle grammar output."""
    spec = allow_input_words("basic_850", "How can a neighbor help?")
    assert (
        make_gbnf(spec, max_words_per_line=9, max_lines=3)
        == make_resources(
            spec,
            max_words_per_line=9,
            max_lines=3,
        ).gbnf
    )


def test_validation() -> None:
    """Ensure compliant and out-of-vocabulary text are distinguished."""
    # The `basic_850` list is still constrained enough that `neighbor` stays out.
    assert is_compliant("The answer is clear.", "basic_850")
    assert "neighbor" in out_of_vocab("The neighbor can help.", "basic_850")


def test_inflected_variants_are_allowed_by_default() -> None:
    """Ensure built-ins accept family variants like `goes` and `made`."""
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
