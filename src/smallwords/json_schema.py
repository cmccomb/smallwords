"""Mirror the package grammar constraints in JSON Schema form.

The schema path is deliberately kept parallel to the GBNF builder so callers
can target runtimes that prefer JSON Schema while keeping the same vocabulary
and shape constraints. Most helpers here build small regex fragments that map
closely to the grammar rules from ``grammar_builder``.
"""

from __future__ import annotations

import re
from typing import Any

from .grammar_builder import ThinkingMode
from .types import WordlistSpec


def _pattern_alt(parts: list[str]) -> str:
    """Join already-escaped alternatives into a non-capturing group.

    Args:
        parts: Already-escaped regex fragments to join.

    Returns:
        A regex fragment that matches any of the supplied parts.
    """
    if len(parts) == 1:
        return parts[0]
    return "(?:" + "|".join(parts) + ")"


def _word_pattern(spec: WordlistSpec) -> str:
    """Build the regex fragment for a single allowed token.

    Args:
        spec: Wordlist specification that defines the allowed tokens.

    Returns:
        A regex fragment for one allowed token.

    Raises:
        ValueError: If the wordlist does not contain any words.
    """
    words = spec.allowed_words()
    if not words:
        raise ValueError("Wordlist must contain at least one word")

    # ``dict.fromkeys`` preserves order while removing duplicates from expansions.
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


def _line_pattern(
    spec: WordlistSpec,
    *,
    min_words_per_line: int,
    max_words_per_line: int,
) -> str:
    """Build the regex fragment for one constrained output line.

    Args:
        spec: Wordlist specification that defines the allowed tokens.
        min_words_per_line: Minimum number of tokens required on one line.
        max_words_per_line: Maximum number of tokens allowed on one line.

    Returns:
        A regex fragment for one constrained output line.
    """
    word = _word_pattern(spec)
    # Lines are modeled as one word followed by a bounded number of space-prefixed words.
    line = word + f"(?: {word}){{{min_words_per_line - 1},{max_words_per_line - 1}}}"

    if spec.line_prefixes:
        prefix = _pattern_alt([re.escape(value) for value in spec.line_prefixes])
        line = f"(?:{prefix})?" + line

    if spec.allowed_punctuation:
        punct = _pattern_alt([re.escape(value) for value in spec.allowed_punctuation])
        line += f"(?:{punct})?"

    return line


def _text_pattern(
    spec: WordlistSpec,
    *,
    min_words_per_line: int,
    max_words_per_line: int,
    max_lines: int,
) -> str:
    """Build the regex fragment for the full text block.

    Args:
        spec: Wordlist specification that defines the allowed tokens.
        min_words_per_line: Minimum number of tokens required on one line.
        max_words_per_line: Maximum number of tokens allowed on one line.
        max_lines: Maximum number of lines allowed in the response body.

    Returns:
        A regex fragment for the full constrained text block.
    """
    line = _line_pattern(
        spec,
        min_words_per_line=min_words_per_line,
        max_words_per_line=max_words_per_line,
    )
    # Multi-line output is encoded directly in the regex so the schema stays self-contained.
    if spec.allow_newlines:
        return line + f"(?:\\n{line}){{0,{max_lines - 1}}}"
    return line


def _response_pattern(
    spec: WordlistSpec,
    *,
    thinking_mode: ThinkingMode,
    min_words_per_line: int,
    max_words_per_line: int,
    max_lines: int,
) -> str:
    """Wrap the text pattern for the selected thinking mode.

    Args:
        spec: Wordlist specification that defines the allowed tokens.
        thinking_mode: Optional wrapper mode for plan/final or thinking/answer output.
        min_words_per_line: Minimum number of tokens required on one line.
        max_words_per_line: Maximum number of tokens allowed on one line.
        max_lines: Maximum number of lines allowed in the response body.

    Returns:
        A full anchored regex pattern for the serialized response body.

    Raises:
        ValueError: If the thinking mode is unsupported.
    """
    text = _text_pattern(
        spec,
        min_words_per_line=min_words_per_line,
        max_words_per_line=max_words_per_line,
        max_lines=max_lines,
    )
    if thinking_mode == "none":
        body = text
    elif thinking_mode == "plan_final":
        body = f"PLAN:\\n{text}\\n\\nFINAL:\\n{text}"
    elif thinking_mode == "thinking_answer":
        body = f"THINKING:\\n{text}\\n\\nANSWER:\\n{text}"
    else:
        raise ValueError(f"Unsupported thinking_mode: {thinking_mode}")
    return f"^{body}$"


def _min_text_length(
    spec: WordlistSpec, *, min_words_per_line: int, max_lines: int
) -> int:
    """Compute the minimum text length for the configured constraint shape.

    Args:
        spec: Wordlist specification that defines the allowed tokens.
        min_words_per_line: Minimum number of tokens required on one line.
        max_lines: Maximum number of lines allowed in the response body.

    Returns:
        The minimum text length for one valid response body.

    Raises:
        ValueError: If the wordlist does not contain any words.
    """
    del max_lines

    words = spec.allowed_words()
    if not words and not spec.allow_numbers:
        raise ValueError("Wordlist must contain at least one word")

    word_min = 1 if spec.allow_numbers else min(len(word) for word in words)
    return word_min + (min_words_per_line - 1) * (1 + word_min)


def _max_text_length(
    spec: WordlistSpec, *, max_words_per_line: int, max_lines: int
) -> int | None:
    """Compute a finite maximum length when the word set is finite.

    Args:
        spec: Wordlist specification that defines the allowed tokens.
        max_words_per_line: Maximum number of tokens allowed on one line.
        max_lines: Maximum number of lines allowed in the response body.

    Returns:
        The maximum text length, or ``None`` when the grammar is unbounded.

    Raises:
        ValueError: If the wordlist does not contain any words.
    """
    if spec.allow_numbers:
        return None

    words = spec.allowed_words()
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
    """Compute the maximum serialized response length for the selected mode.

    Args:
        spec: Wordlist specification that defines the allowed tokens.
        thinking_mode: Optional wrapper mode for plan/final or thinking/answer output.
        max_words_per_line: Maximum number of tokens allowed on one line.
        max_lines: Maximum number of lines allowed in the response body.

    Returns:
        The maximum serialized response length, or ``None`` when unbounded.

    Raises:
        ValueError: If the thinking mode is unsupported.
    """
    text_max = _max_text_length(
        spec, max_words_per_line=max_words_per_line, max_lines=max_lines
    )
    if text_max is None:
        return None
    # Wrapper labels contribute a fixed overhead on top of the text body length.
    if thinking_mode == "none":
        return text_max
    if thinking_mode == "plan_final":
        return len("PLAN:\n") + text_max + len("\n\nFINAL:\n") + text_max
    if thinking_mode == "thinking_answer":
        return len("THINKING:\n") + text_max + len("\n\nANSWER:\n") + text_max
    raise ValueError(f"Unsupported thinking_mode: {thinking_mode}")


def _min_response_length(
    spec: WordlistSpec,
    *,
    thinking_mode: ThinkingMode,
    min_words_per_line: int,
    max_lines: int,
) -> int:
    """Compute the minimum serialized response length for the selected mode.

    Args:
        spec: Wordlist specification that defines the allowed tokens.
        thinking_mode: Optional wrapper mode for plan/final or thinking/answer output.
        min_words_per_line: Minimum number of tokens required on one line.
        max_lines: Maximum number of lines allowed in the response body.

    Returns:
        The minimum serialized response length.

    Raises:
        ValueError: If the thinking mode is unsupported.
    """
    text_min = _min_text_length(
        spec, min_words_per_line=min_words_per_line, max_lines=max_lines
    )
    # Wrapper labels contribute a fixed overhead on top of the minimum text body length.
    if thinking_mode == "none":
        return text_min
    if thinking_mode == "plan_final":
        return len("PLAN:\n") + text_min + len("\n\nFINAL:\n") + text_min
    if thinking_mode == "thinking_answer":
        return len("THINKING:\n") + text_min + len("\n\nANSWER:\n") + text_min
    raise ValueError(f"Unsupported thinking_mode: {thinking_mode}")


def build_json_schema(
    spec: WordlistSpec,
    *,
    key: str = "text",
    title: str | None = None,
    description: str | None = None,
    thinking_mode: ThinkingMode = "none",
    min_words_per_line: int = 1,
    max_words_per_line: int = 40,
    max_lines: int = 8,
) -> dict[str, Any]:
    """Build a strict single-key JSON Schema mirroring the grammar constraints.

    Args:
        spec: Wordlist specification that defines the allowed tokens.
        key: Property name for the generated single-key object schema.
        title: Optional schema title override.
        description: Optional schema description override for the value field.
        thinking_mode: Optional wrapper mode for plan/final or thinking/answer output.
        min_words_per_line: Minimum number of tokens required on one line.
        max_words_per_line: Maximum number of tokens allowed on one line.
        max_lines: Maximum number of lines allowed in the response body.

    Returns:
        A strict single-key JSON Schema aligned with the grammar constraints.

    Raises:
        ValueError: If the key or limits are invalid.
    """
    if not key:
        raise ValueError("key must be a non-empty string")
    if min_words_per_line < 1:
        raise ValueError("min_words_per_line must be >= 1")
    if max_words_per_line < 1:
        raise ValueError("max_words_per_line must be >= 1")
    if min_words_per_line > max_words_per_line:
        raise ValueError("min_words_per_line must be <= max_words_per_line")
    if max_lines < 1:
        raise ValueError("max_lines must be >= 1")

    # The value schema is built first so callers can override just the outer key/title.
    value_schema: dict[str, Any] = {
        "type": "string",
        "pattern": _response_pattern(
            spec,
            thinking_mode=thinking_mode,
            min_words_per_line=min_words_per_line,
            max_words_per_line=max_words_per_line,
            max_lines=max_lines,
        ),
        "minLength": _min_response_length(
            spec,
            thinking_mode=thinking_mode,
            min_words_per_line=min_words_per_line,
            max_lines=max_lines,
        ),
        "description": description
        or f"Response text constrained to the {spec.name} word list.",
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

    # The outer object stays strict so downstream structured-output APIs behave predictably.
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": title or f"{spec.name}_response",
        "type": "object",
        "properties": {key: value_schema},
        "required": [key],
        "additionalProperties": False,
    }
