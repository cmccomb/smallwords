"""Turn a wordlist specification into a concrete GBNF grammar string.

This module is the hard-constraint half of the package. It takes the normalized
and expanded vocabulary surface from ``WordlistSpec`` and emits a grammar that
mirrors the same line, punctuation, capitalization, and thinking-mode rules
used by the rest of the stack.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from .types import WordlistSpec

# These wrapper modes let callers ask for visible planning blocks around the answer.
ThinkingMode = Literal["none", "plan_final", "thinking_answer"]


def _esc(text: str) -> str:
    """Escape characters that need quoting inside a GBNF string literal.

    Args:
        text: Literal text that will be inserted into the grammar.

    Returns:
        The escaped literal text ready for inclusion in GBNF quotes.
    """
    return text.replace("\\", "\\\\").replace('"', '\\"')


@lru_cache(maxsize=128)
def build_gbnf(
    spec: WordlistSpec,
    *,
    thinking_mode: ThinkingMode = "none",
    max_words_per_line: int = 40,
    max_lines: int = 8,
) -> str:
    """Build a GBNF grammar string for a controlled-vocabulary output mode.

    Args:
        spec: Wordlist specification that defines the allowed tokens.
        thinking_mode: Optional wrapper mode for plan/final or thinking/answer output.
        max_words_per_line: Maximum number of tokens allowed on one line.
        max_lines: Maximum number of lines allowed in the response body.

    Returns:
        The generated GBNF grammar string.

    Raises:
        ValueError: If the limits are invalid, the wordlist is empty, or the
            thinking mode is unsupported.
    """
    if max_words_per_line < 1:
        raise ValueError("max_words_per_line must be >= 1")
    if max_lines < 1:
        raise ValueError("max_lines must be >= 1")

    words = spec.allowed_words()
    if not words:
        raise ValueError("Wordlist must contain at least one word")

    # Pre-rendering the alternatives keeps the final rule list easier to read.
    common_word_alts = " |\n  ".join(f'"{_esc(word)}"' for word in words)

    rules: list[str] = []
    # The root rule determines whether the caller wants a plain response or a
    # two-block format that exposes a short planning/thinking section first.
    if thinking_mode == "none":
        rules.append("root ::= text")
    elif thinking_mode == "plan_final":
        rules.append(
            'root ::= "PLAN:" newline text newline newline "FINAL:" newline text'
        )
    elif thinking_mode == "thinking_answer":
        rules.append(
            'root ::= "THINKING:" newline text newline newline "ANSWER:" newline text'
        )
    else:
        raise ValueError(f"Unsupported thinking_mode: {thinking_mode}")

    if spec.line_prefixes:
        line_rule = (
            f"line ::= line-prefix? word (space word){{0,{max_words_per_line - 1}}}"
        )
    else:
        line_rule = f"line ::= word (space word){{0,{max_words_per_line - 1}}}"
    if spec.allowed_punctuation:
        line_rule += " punct?"

    # The word rule is assembled dynamically so optional features stay aligned.
    word_rules = ["common-word"]
    if spec.allow_capitalized_words:
        word_rules.append("capitalized-word")
    if spec.allow_numbers:
        word_rules.append("number")

    word_rule = " |\n  ".join(word_rules)

    rules.extend(
        [
            # Text is either a single line or a repeated newline-separated line block.
            f"text ::= line (newline line){{0,{max_lines - 1}}}"
            if spec.allow_newlines
            else "text ::= line",
            line_rule,
            'space ::= " "',
            'newline ::= "\\n"',
            f"word ::=\n  {word_rule}",
            f"common-word ::=\n  {common_word_alts}",
        ]
    )

    if spec.allow_capitalized_words:
        # Capitalized words are generated explicitly so grammar engines do not infer casing.
        cap_alts = " |\n  ".join(f'"{_esc(word.capitalize())}"' for word in words)
        rules.append(f"capitalized-word ::=\n  {cap_alts}")

    if spec.allow_numbers:
        # Numbers stay intentionally broad because the validator/schema treat them the same way.
        rules.append("number ::= [0-9]+")

    if spec.allowed_punctuation:
        punct_alts = " | ".join(f'"{_esc(ch)}"' for ch in spec.allowed_punctuation)
        rules.append(f"punct ::= {punct_alts}")

    # Prefixes stay optional in `line`, but defining the rule keeps the grammar
    # shape consistent for callers that want bullets or numbered steps.
    if spec.line_prefixes:
        prefix_alts = " | ".join(f'"{_esc(prefix)}"' for prefix in spec.line_prefixes)
        rules.append(f"line-prefix ::= {prefix_alts}")

    return "\n\n".join(rules) + "\n"
