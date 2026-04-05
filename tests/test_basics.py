"""Basic smoke tests for prompts, grammars, and validation helpers."""

from smallwords import COMMON_50, is_compliant, out_of_vocab, prompt_explain_simply


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
