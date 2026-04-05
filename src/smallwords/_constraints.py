"""Compile a wordlist and output shape into one shared constraint model."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

from .types import OutputShape, WordlistSpec

_WRAPPER_LABELS: dict[str, tuple[str, ...]] = {
    "none": (),
    "plan_final": ("PLAN:", "FINAL:"),
    "thinking_answer": ("THINKING:", "ANSWER:"),
}


@dataclass(frozen=True)
class CompiledConstraints:
    """Store the shared constraint data used by every serializer."""

    spec: WordlistSpec
    shape: OutputShape
    words: tuple[str, ...]
    capitalized_words: tuple[str, ...]
    wrapper_labels: tuple[str, ...]
    word_pattern: str
    line_pattern: str
    text_pattern: str
    response_pattern: str
    min_text_length: int
    max_text_length: int | None
    min_response_length: int
    max_response_length: int | None


def validate_output_shape(shape: OutputShape) -> None:
    """Reject unsupported response limits or wrapper modes."""
    if shape.thinking_mode not in _WRAPPER_LABELS:
        raise ValueError(f"Unsupported thinking_mode: {shape.thinking_mode}")
    if shape.min_words_per_line < 1:
        raise ValueError("min_words_per_line must be >= 1")
    if shape.max_words_per_line < 1:
        raise ValueError("max_words_per_line must be >= 1")
    if shape.min_words_per_line > shape.max_words_per_line:
        raise ValueError("min_words_per_line must be <= max_words_per_line")
    if shape.max_lines < 1:
        raise ValueError("max_lines must be >= 1")


def _pattern_alt(parts: list[str]) -> str:
    """Join already-escaped alternatives into a non-capturing group."""
    if len(parts) == 1:
        return parts[0]
    return "(?:" + "|".join(parts) + ")"


def _min_text_length(
    spec: WordlistSpec, *, shape: OutputShape, words: tuple[str, ...]
) -> int:
    """Compute the minimum text length for one valid response body."""
    if not words and not spec.allow_numbers:
        raise ValueError("Wordlist must contain at least one word")
    word_min = 1 if spec.allow_numbers else min(len(word) for word in words)
    return word_min + (shape.min_words_per_line - 1) * (1 + word_min)


def _max_text_length(
    spec: WordlistSpec, *, shape: OutputShape, words: tuple[str, ...]
) -> int | None:
    """Compute a finite maximum length when the grammar is bounded."""
    if spec.allow_numbers:
        return None
    if not words:
        raise ValueError("Wordlist must contain at least one word")

    word_max = max(len(word) for word in words)
    prefix_max = max((len(prefix) for prefix in spec.line_prefixes), default=0)
    punct_max = max((len(punct) for punct in spec.allowed_punctuation), default=0)

    line_max = prefix_max + word_max
    if shape.max_words_per_line > 1:
        line_max += (shape.max_words_per_line - 1) * (1 + word_max)
    line_max += punct_max

    if spec.allow_newlines:
        return line_max + (shape.max_lines - 1) * (1 + line_max)
    return line_max


def _response_length(
    *,
    thinking_mode: str,
    text_length: int | None,
    minimum: bool,
) -> int | None:
    """Add wrapper overhead to a text length estimate."""
    if text_length is None:
        return None
    labels = _WRAPPER_LABELS[thinking_mode]
    if not labels:
        return text_length
    first, second = labels
    return len(first + "\n") + text_length + len("\n\n" + second + "\n") + text_length


@lru_cache(maxsize=128)
def compile_constraints(spec: WordlistSpec, shape: OutputShape) -> CompiledConstraints:
    """Compile one spec-plus-shape pair into the shared constraint model."""
    validate_output_shape(shape)

    words = spec.allowed_words()
    if not words and not spec.allow_numbers:
        raise ValueError("Wordlist must contain at least one word")

    capitalized_words = ()
    if spec.allow_capitalized_words:
        capitalized_words = tuple(
            dict.fromkeys(word.capitalize() for word in words if word.capitalize() != word)
        )

    word_parts = [re.escape(word) for word in words]
    word_parts.extend(re.escape(word) for word in capitalized_words)
    if spec.allow_numbers:
        word_parts.append(r"\d+")
    word_pattern = _pattern_alt(word_parts)

    line_pattern = (
        word_pattern
        + f"(?: {word_pattern})"
        + "{"
        + f"{shape.min_words_per_line - 1},{shape.max_words_per_line - 1}"
        + "}"
    )
    if spec.line_prefixes:
        prefix = _pattern_alt([re.escape(value) for value in spec.line_prefixes])
        line_pattern = f"(?:{prefix})?" + line_pattern
    if spec.allowed_punctuation:
        punct = _pattern_alt([re.escape(value) for value in spec.allowed_punctuation])
        line_pattern += f"(?:{punct})?"

    if spec.allow_newlines:
        text_pattern = line_pattern + f"(?:\\n{line_pattern}){{0,{shape.max_lines - 1}}}"
    else:
        text_pattern = line_pattern

    wrapper_labels = _WRAPPER_LABELS[shape.thinking_mode]
    if not wrapper_labels:
        response_pattern = f"^{text_pattern}$"
    else:
        first, second = wrapper_labels
        response_pattern = f"^{first}\\n{text_pattern}\\n\\n{second}\\n{text_pattern}$"

    min_text_length = _min_text_length(spec, shape=shape, words=words)
    max_text_length = _max_text_length(spec, shape=shape, words=words)

    return CompiledConstraints(
        spec=spec,
        shape=shape,
        words=words,
        capitalized_words=capitalized_words,
        wrapper_labels=wrapper_labels,
        word_pattern=word_pattern,
        line_pattern=line_pattern,
        text_pattern=text_pattern,
        response_pattern=response_pattern,
        min_text_length=min_text_length,
        max_text_length=max_text_length,
        min_response_length=_response_length(
            thinking_mode=shape.thinking_mode,
            text_length=min_text_length,
            minimum=True,
        )
        or 0,
        max_response_length=_response_length(
            thinking_mode=shape.thinking_mode,
            text_length=max_text_length,
            minimum=False,
        ),
    )
