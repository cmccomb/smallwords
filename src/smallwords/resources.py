"""Build the portable resource bundle that most callers actually consume.

``OutputResources`` is the package's main runtime-facing abstraction. It keeps a
wordlist and its output-shaping limits together, then lazily produces matching
GBNF and JSON Schema artifacts so callers do not have to coordinate those
formats by hand.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cached_property
from typing import Any

from ._spec_utils import resolve_wordlist_spec
from .grammar_builder import ThinkingMode, build_gbnf
from .json_schema import build_json_schema
from .types import WordlistSpec
from .wordlists import (
    BASIC_850_SPEC,
    CAVEMAN_898_SPEC,
    MOBY_898_SPEC,
    PIRATE_898_SPEC,
    SPECIAL_ENGLISH_1475_SPEC,
)


@dataclass(frozen=True)
class OutputResources:
    """Portable GBNF and JSON Schema resources for a specific word list.

    Attributes:
        spec: Wordlist specification used for every generated resource.
        thinking_mode: Optional wrapper mode for plan/final or thinking/answer output.
        max_words_per_line: Maximum number of tokens allowed on one line.
        max_lines: Maximum number of lines allowed in the response body.
    """

    spec: WordlistSpec
    thinking_mode: ThinkingMode = "none"
    max_words_per_line: int = 40
    max_lines: int = 8

    @cached_property
    def gbnf(self) -> str:
        """Compile the configured word list into a GBNF string on first access.

        Returns:
            The generated GBNF grammar string for this resource bundle.
        """
        # Grammar generation is cached because many callers read the property repeatedly.
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
        """Build a strict single-key JSON Schema matching these limits.

        Args:
            key: Property name for the generated single-key object schema.
            title: Optional schema title override.
            description: Optional schema description override for the value field.

        Returns:
            A JSON Schema dictionary aligned with this resource bundle.
        """
        # Schema generation stays parameterized so callers can rename the single value key.
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
        """Write the generated GBNF resource to disk.

        Args:
            path: Destination path for the grammar file.
        """
        # Persisting resources to disk makes them easy to hand off to other runtimes.
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
        """Write the generated JSON Schema resource to disk.

        Args:
            path: Destination path for the schema file.
            key: Property name for the generated single-key object schema.
            title: Optional schema title override.
            description: Optional schema description override for the value field.
        """
        # JSON output is indented so checked-in artifacts stay readable in diffs.
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(
                self.json_schema(key=key, title=title, description=description),
                handle,
                indent=2,
            )
            handle.write("\n")


# These shared presets cover the named built-ins most callers reach for first.
# This preset bundles resources for the full normalized Moby vocabulary.
MOBY_898 = OutputResources(MOBY_898_SPEC)
# This preset bundles resources for the Basic English vocabulary.
BASIC_850 = OutputResources(BASIC_850_SPEC)
# This preset bundles resources for the caveman remix vocabulary.
CAVEMAN_898 = OutputResources(CAVEMAN_898_SPEC)
# This preset bundles resources for the pirate remix vocabulary.
PIRATE_898 = OutputResources(PIRATE_898_SPEC)
# This preset bundles resources for the Special English vocabulary.
SPECIAL_ENGLISH_1475 = OutputResources(SPECIAL_ENGLISH_1475_SPEC)


def make_resources(
    wordlist: str | WordlistSpec,
    *,
    thinking_mode: ThinkingMode = "none",
    max_words_per_line: int = 40,
    max_lines: int = 8,
) -> OutputResources:
    """Build output resources from either a named or inline word list spec.

    Args:
        wordlist: Built-in wordlist name or inline wordlist specification.
        thinking_mode: Optional wrapper mode for plan/final or thinking/answer output.
        max_words_per_line: Maximum number of tokens allowed on one line.
        max_lines: Maximum number of lines allowed in the response body.

    Returns:
        A ready-to-use resource bundle for the selected wordlist.
    """
    # Resolve named presets late so callers can also pass an inline spec object.
    spec = resolve_wordlist_spec(wordlist)
    # The factory mirrors ``OutputResources`` directly so its behavior stays unsurprising.
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
    """Build JSON Schema directly from a named or inline word list spec.

    Args:
        wordlist: Built-in wordlist name or inline wordlist specification.
        key: Property name for the generated single-key object schema.
        title: Optional schema title override.
        description: Optional schema description override for the value field.
        thinking_mode: Optional wrapper mode for plan/final or thinking/answer output.
        max_words_per_line: Maximum number of tokens allowed on one line.
        max_lines: Maximum number of lines allowed in the response body.

    Returns:
        A JSON Schema dictionary aligned with the selected wordlist.
    """
    # This helper keeps schema-only callers on the same code path as bundle users.
    return make_resources(
        wordlist,
        thinking_mode=thinking_mode,
        max_words_per_line=max_words_per_line,
        max_lines=max_lines,
    ).json_schema(key=key, title=title, description=description)


def make_gbnf(
    wordlist: str | WordlistSpec,
    *,
    thinking_mode: ThinkingMode = "none",
    max_words_per_line: int = 40,
    max_lines: int = 8,
) -> str:
    """Build GBNF directly from a named or inline word list spec.

    Args:
        wordlist: Built-in wordlist name or inline wordlist specification.
        thinking_mode: Optional wrapper mode for plan/final or thinking/answer output.
        max_words_per_line: Maximum number of tokens allowed on one line.
        max_lines: Maximum number of lines allowed in the response body.

    Returns:
        A GBNF string aligned with the selected wordlist.
    """
    # This helper mirrors ``make_json_schema`` so direct-export callers get a
    # consistent top-level API across both portable resource formats.
    return make_resources(
        wordlist,
        thinking_mode=thinking_mode,
        max_words_per_line=max_words_per_line,
        max_lines=max_lines,
    ).gbnf
