"""Serialize compiled constraints into GBNF."""

from __future__ import annotations

from ._constraints import compile_constraints
from .types import OutputShape, WordlistSpec


def _esc(text: str) -> str:
    """Escape characters that need quoting inside a GBNF string literal."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


def build_gbnf(spec: WordlistSpec, *, shape: OutputShape) -> str:
    """Build a GBNF grammar string for a wordlist and output shape."""
    constraints = compile_constraints(spec, shape)

    rules: list[str] = []
    if not constraints.wrapper_labels:
        rules.append("root ::= text")
    else:
        first, second = constraints.wrapper_labels
        rules.append(
            f'root ::= "{_esc(first)}" newline text newline newline "{_esc(second)}" newline text'
        )

    repeat_range = (
        "{"
        + f"{shape.min_words_per_line - 1},{shape.max_words_per_line - 1}"
        + "}"
    )
    if spec.line_prefixes:
        line_rule = f"line ::= line-prefix? word (space word){repeat_range}"
    else:
        line_rule = f"line ::= word (space word){repeat_range}"
    if spec.allowed_punctuation:
        line_rule += " punct?"

    word_rules: list[str] = []
    if constraints.words:
        word_rules.append("common-word")
    if constraints.capitalized_words:
        word_rules.append("capitalized-word")
    if spec.allow_numbers:
        word_rules.append("number")

    rules.extend(
        [
            f"text ::= line (newline line){{0,{shape.max_lines - 1}}}"
            if spec.allow_newlines
            else "text ::= line",
            line_rule,
            'space ::= " "',
            'newline ::= "\\n"',
            "word ::=\n  " + " |\n  ".join(word_rules),
        ]
    )

    if constraints.words:
        common_word_alts = " |\n  ".join(f'"{_esc(word)}"' for word in constraints.words)
        rules.append(f"common-word ::=\n  {common_word_alts}")

    if constraints.capitalized_words:
        cap_alts = " |\n  ".join(
            f'"{_esc(word)}"' for word in constraints.capitalized_words
        )
        rules.append(f"capitalized-word ::=\n  {cap_alts}")

    if spec.allow_numbers:
        rules.append("number ::= [0-9]+")

    if spec.allowed_punctuation:
        punct_alts = " | ".join(f'"{_esc(ch)}"' for ch in spec.allowed_punctuation)
        rules.append(f"punct ::= {punct_alts}")

    if spec.line_prefixes:
        prefix_alts = " | ".join(f'"{_esc(prefix)}"' for prefix in spec.line_prefixes)
        rules.append(f"line-prefix ::= {prefix_alts}")

    return "\n\n".join(rules) + "\n"
