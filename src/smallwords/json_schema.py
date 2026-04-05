"""JSON Schema builders for constrained structured outputs."""

from __future__ import annotations

import re
from typing import Any

from .grammar_builder import ThinkingMode
from .types import WordlistSpec


def _pattern_alt(parts: list[str]) -> str:
    """Join already-escaped alternatives into a non-capturing group."""
    if len(parts) == 1:
        return parts[0]
    return "(?:" + "|".join(parts) + ")"


def _word_pattern(spec: WordlistSpec) -> str:
    """Build the regex fragment for a single allowed token."""
    words = spec.normalized_words()
    if not words:
        raise ValueError("Wordlist must contain at least one word")

    variants = list(dict.fromkeys(re.escape(word) for word in words))
    if spec.allow_capitalized_words:
        variants.extend(
            variant
            for variant in (re.escape(word.capitalize()) for word in words)
            if variant not in variants
        )
    if spec.allow_numbers:
        variants.append(r"\d+")
    return _pattern_alt(variants)


def _line_pattern(spec: WordlistSpec, *, max_words_per_line: int) -> str:
    """Build the regex fragment for one constrained output line."""
    word = _word_pattern(spec)
    line = word + f"(?: {word}){{0,{max_words_per_line - 1}}}"

    if spec.line_prefixes:
        prefix = _pattern_alt([re.escape(value) for value in spec.line_prefixes])
        line = f"(?:{prefix})?" + line

    if spec.allowed_punctuation:
        punct = _pattern_alt([re.escape(value) for value in spec.allowed_punctuation])
        line += f"(?:{punct})?"

    return line


def _text_pattern(spec: WordlistSpec, *, max_words_per_line: int, max_lines: int) -> str:
    """Build the regex fragment for the full text block."""
    line = _line_pattern(spec, max_words_per_line=max_words_per_line)
    if spec.allow_newlines:
        return line + f"(?:\\n{line}){{0,{max_lines - 1}}}"
    return line


def _response_pattern(
    spec: WordlistSpec,
    *,
    thinking_mode: ThinkingMode,
    max_words_per_line: int,
    max_lines: int,
) -> str:
    """Wrap the text pattern for the selected thinking mode."""
    text = _text_pattern(spec, max_words_per_line=max_words_per_line, max_lines=max_lines)
    if thinking_mode == "none":
        body = text
    elif thinking_mode == "plan_final":
        body = f"PLAN:\\n{text}\\n\\nFINAL:\\n{text}"
    elif thinking_mode == "thinking_answer":
        body = f"THINKING:\\n{text}\\n\\nANSWER:\\n{text}"
    else:
        raise ValueError(f"Unsupported thinking_mode: {thinking_mode}")
    return f"^{body}$"


def _max_text_length(spec: WordlistSpec, *, max_words_per_line: int, max_lines: int) -> int | None:
    """Compute a finite maximum length when the word set is finite."""
    if spec.allow_numbers:
        return None

    words = spec.normalized_words()
    if not words:
        raise ValueError("Wordlist must contain at least one word")

    word_max = max(len(word) for word in words)
    prefix_max = max((len(prefix) for prefix in spec.line_prefixes), default=0)
    punct_max = max((len(punct) for punct in spec.allowed_punctuation), default=0)

    line_max = prefix_max + word_max
    if max_words_per_line > 1:
        line_max += (max_words_per_line - 1) * (1 + word_max)
    line_max += punct_max

    if spec.allow_newlines:
        text_max = line_max + (max_lines - 1) * (1 + line_max)
    else:
        text_max = line_max

    return text_max


def _max_response_length(
    spec: WordlistSpec,
    *,
    thinking_mode: ThinkingMode,
    max_words_per_line: int,
    max_lines: int,
) -> int | None:
    """Compute the maximum serialized response length for the selected mode."""
    text_max = _max_text_length(spec, max_words_per_line=max_words_per_line, max_lines=max_lines)
    if text_max is None:
        return None
    if thinking_mode == "none":
        return text_max
    if thinking_mode == "plan_final":
        return len("PLAN:\n") + text_max + len("\n\nFINAL:\n") + text_max
    if thinking_mode == "thinking_answer":
        return len("THINKING:\n") + text_max + len("\n\nANSWER:\n") + text_max
    raise ValueError(f"Unsupported thinking_mode: {thinking_mode}")


def build_json_schema(
    spec: WordlistSpec,
    *,
    key: str = "text",
    title: str | None = None,
    description: str | None = None,
    thinking_mode: ThinkingMode = "none",
    max_words_per_line: int = 40,
    max_lines: int = 8,
) -> dict[str, Any]:
    """Build a strict single-key JSON Schema mirroring the grammar constraints."""
    if not key:
        raise ValueError("key must be a non-empty string")
    if max_words_per_line < 1:
        raise ValueError("max_words_per_line must be >= 1")
    if max_lines < 1:
        raise ValueError("max_lines must be >= 1")

    value_schema: dict[str, Any] = {
        "type": "string",
        "pattern": _response_pattern(
            spec,
            thinking_mode=thinking_mode,
            max_words_per_line=max_words_per_line,
            max_lines=max_lines,
        ),
        "minLength": 1,
        "description": description or f"Response text constrained to the {spec.name} word list.",
    }

    max_length = _max_response_length(
        spec,
        thinking_mode=thinking_mode,
        max_words_per_line=max_words_per_line,
        max_lines=max_lines,
    )
    # `maxLength` is omitted when numbers are allowed because the regex then
    # permits arbitrarily long numeric tokens.
    if max_length is not None:
        value_schema["maxLength"] = max_length

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": title or f"{spec.name}_response",
        "type": "object",
        "properties": {key: value_schema},
        "required": [key],
        "additionalProperties": False,
    }
