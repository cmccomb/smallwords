from __future__ import annotations

from functools import lru_cache
from typing import Literal

from .types import WordlistSpec

ThinkingMode = Literal["none", "plan_final", "thinking_answer"]


def _esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


@lru_cache(maxsize=128)
def build_gbnf(
    spec: WordlistSpec,
    *,
    thinking_mode: ThinkingMode = "none",
    max_words_per_line: int = 40,
    max_lines: int = 8,
) -> str:
    """Build a GBNF grammar string for a controlled-vocabulary output mode."""
    if max_words_per_line < 1:
        raise ValueError("max_words_per_line must be >= 1")
    if max_lines < 1:
        raise ValueError("max_lines must be >= 1")

    words = spec.normalized_words()
    if not words:
        raise ValueError("Wordlist must contain at least one word")

    common_word_alts = " |\n  ".join(f'"{_esc(word)}"' for word in words)

    rules: list[str] = []
    if thinking_mode == "none":
        rules.append('root ::= text')
    elif thinking_mode == "plan_final":
        rules.append('root ::= "PLAN:" newline text newline newline "FINAL:" newline text')
    elif thinking_mode == "thinking_answer":
        rules.append('root ::= "THINKING:" newline text newline newline "ANSWER:" newline text')
    else:
        raise ValueError(f"Unsupported thinking_mode: {thinking_mode}")

    rules.extend(
        [
            f'text ::= line (newline line){{0,{max_lines - 1}}}',
            f'line ::= [line_prefix] word (space word){{0,{max_words_per_line - 1}}} [punct]',
            'space ::= " "',
            'newline ::= "\\n"',
            'word ::= common_word | capitalized_word' if spec.allow_capitalized_words else 'word ::= common_word',
            f'common_word ::=\n  {common_word_alts}',
        ]
    )

    if spec.allow_capitalized_words:
        cap_alts = " |\n  ".join(f'"{_esc(word.capitalize())}"' for word in words)
        rules.append(f'capitalized_word ::=\n  {cap_alts}')

    if spec.allowed_punctuation:
        punct_alts = " | ".join(f'"{_esc(ch)}"' for ch in spec.allowed_punctuation)
        rules.append(f'punct ::= {punct_alts}')
    else:
        rules.append('punct ::= "."')

    if spec.line_prefixes:
        prefix_alts = " | ".join(f'"{_esc(prefix)}"' for prefix in spec.line_prefixes)
        rules.append(f'line_prefix ::= {prefix_alts}')
    else:
        rules.append('line_prefix ::= "- "')

    if spec.allow_numbers:
        rules.append('number ::= [0-9]+')

    return "\n\n".join(rules) + "\n"
