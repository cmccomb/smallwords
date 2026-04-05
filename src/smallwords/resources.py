"""Portable constrained-output resources built from a word list."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cached_property
from typing import Any

from .grammar_builder import ThinkingMode, build_gbnf
from .json_schema import build_json_schema
from .types import WordlistSpec
from .wordlists import (
    BASIC_850_SPEC,
    COMMON_50_SPEC,
    COMMON_100_SPEC,
    COMMON_250_SPEC,
    REASONING_250_SPEC,
    SPECIAL_ENGLISH_SPEC,
    get_wordlist,
)


@dataclass(frozen=True)
class OutputResources:
    """Portable GBNF and JSON Schema resources for a specific word list."""

    spec: WordlistSpec
    thinking_mode: ThinkingMode = "none"
    max_words_per_line: int = 40
    max_lines: int = 8

    @cached_property
    def gbnf(self) -> str:
        """Compile the configured word list into a GBNF string on first access."""
        return build_gbnf(
            self.spec,
            thinking_mode=self.thinking_mode,
            max_words_per_line=self.max_words_per_line,
            max_lines=self.max_lines,
        )

    def json_schema(
        self,
        *,
        key: str = "text",
        title: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Build a strict single-key JSON Schema matching these limits."""
        return build_json_schema(
            self.spec,
            key=key,
            title=title,
            description=description,
            thinking_mode=self.thinking_mode,
            max_words_per_line=self.max_words_per_line,
            max_lines=self.max_lines,
        )

    def save_gbnf(self, path: str) -> None:
        """Write the generated GBNF resource to disk."""
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(self.gbnf)

    def save_json_schema(
        self,
        path: str,
        *,
        key: str = "text",
        title: str | None = None,
        description: str | None = None,
    ) -> None:
        """Write the generated JSON Schema resource to disk."""
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(
                self.json_schema(key=key, title=title, description=description),
                handle,
                indent=2,
            )
            handle.write("\n")


# These shared presets cover the named built-ins most callers reach for first.
COMMON_50 = OutputResources(COMMON_50_SPEC)
COMMON_100 = OutputResources(COMMON_100_SPEC)
COMMON_250 = OutputResources(COMMON_250_SPEC)
BASIC_850 = OutputResources(BASIC_850_SPEC)
REASONING_250 = OutputResources(REASONING_250_SPEC)
SPECIAL_ENGLISH = OutputResources(SPECIAL_ENGLISH_SPEC)

COMMON_50_THINKING = OutputResources(COMMON_50_SPEC, thinking_mode="plan_final")
COMMON_100_THINKING = OutputResources(COMMON_100_SPEC, thinking_mode="plan_final")
COMMON_250_THINKING = OutputResources(COMMON_250_SPEC, thinking_mode="thinking_answer")


def make_resources(
    wordlist: str | WordlistSpec,
    *,
    thinking_mode: ThinkingMode = "none",
    max_words_per_line: int = 40,
    max_lines: int = 8,
) -> OutputResources:
    """Build output resources from either a named or inline word list spec."""
    # Resolve named presets late so callers can also pass an inline spec object.
    spec = get_wordlist(wordlist) if isinstance(wordlist, str) else wordlist
    return OutputResources(
        spec=spec,
        thinking_mode=thinking_mode,
        max_words_per_line=max_words_per_line,
        max_lines=max_lines,
    )


def make_json_schema(
    wordlist: str | WordlistSpec,
    *,
    key: str = "text",
    title: str | None = None,
    description: str | None = None,
    thinking_mode: ThinkingMode = "none",
    max_words_per_line: int = 40,
    max_lines: int = 8,
) -> dict[str, Any]:
    """Build JSON Schema directly from a named or inline word list spec."""
    return make_resources(
        wordlist,
        thinking_mode=thinking_mode,
        max_words_per_line=max_words_per_line,
        max_lines=max_lines,
    ).json_schema(key=key, title=title, description=description)
