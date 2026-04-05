"""Basic smoke tests for prompts, grammars, and validation helpers."""

from smallwords import (
    COMMON_50,
    WordFamily,
    WordlistSpec,
    is_compliant,
    out_of_vocab,
    prompt_explain_simply,
)


def test_prompt_mentions_wordlist() -> None:
    """Ensure the prompt text names the selected built-in wordlist."""
    prompt = prompt_explain_simply("How does rain work?", wordlist="common_50")
    assert "common_50" in prompt


def test_gbnf_has_root() -> None:
    """Ensure prebuilt resources expose a top-level GBNF root rule."""
    assert COMMON_50.gbnf.startswith("root ::= text")


def test_validation() -> None:
    """Ensure compliant and out-of-vocabulary text are distinguished."""
    # The `common_50` list is intentionally strict, so `bridge` stays out.
    assert is_compliant("The man can make it.", "common_50")
    assert "bridge" in out_of_vocab("The man can make a bridge.", "common_50")


def test_inflected_variants_are_allowed_by_default() -> None:
    """Ensure built-ins accept family variants like `goes` and `made`."""
    assert is_compliant("He goes out.", "common_250")
    assert is_compliant("The man made it.", "common_50")


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
