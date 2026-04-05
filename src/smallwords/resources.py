"""Expose the portable resource bundle used by constrained text workflows."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import cached_property
from os import PathLike
from typing import Any

from ._spec_utils import resolve_wordlist_spec
from .grammar_builder import build_gbnf
from .json_schema import build_json_schema
from .types import OutputShape, WordlistSpec


@dataclass(frozen=True)
class OutputResources:
    """Portable GBNF and JSON Schema resources for a specific wordlist and shape.

    Attributes:
        spec: Wordlist specification used for every generated resource.
        shape: Serialized response shape shared by the grammar and schema.
    """

    spec: WordlistSpec
    shape: OutputShape = field(default_factory=OutputShape)

    @classmethod
    def from_wordlist(
        cls,
        wordlist: str | WordlistSpec,
        *,
        shape: OutputShape | None = None,
    ) -> OutputResources:
        """Resolve a named or inline wordlist into a resource bundle."""
        return cls(spec=resolve_wordlist_spec(wordlist), shape=shape or OutputShape())

    @cached_property
    def gbnf(self) -> str:
        """Compile the configured wordlist and shape into a GBNF string."""
        return build_gbnf(self.spec, shape=self.shape)

    def json_schema(
        self,
        *,
        key: str = "text",
        title: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Build a strict single-key JSON Schema aligned with this resource bundle."""
        return build_json_schema(
            self.spec,
            shape=self.shape,
            key=key,
            title=title,
            description=description,
        )

    def save_gbnf(self, path: str | PathLike[str]) -> None:
        """Write the generated GBNF resource to disk."""
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(self.gbnf)

    def save_json_schema(
        self,
        path: str | PathLike[str],
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
