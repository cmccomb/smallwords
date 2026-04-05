"""Shared helpers for building prompt-and-grammar example requests."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

# Keep repo-local example runs pointed at `src/` instead of an older installed build.
SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

if TYPE_CHECKING:
    from smallwords import OutputResources


@dataclass(frozen=True)
class ExampleRequest:
    """Bundle the prompt and constraint resources a runtime would use together."""

    prompt: str
    grammar: str
    schema: dict[str, Any]

    def summary(self) -> dict[str, Any]:
        """Return a compact summary of the bundled prompt-and-grammar request."""
        schema_key = next(iter(self.schema["properties"]))
        return {
            "prompt": self.prompt,
            "schema_key": schema_key,
            "grammar_rule_count": self.grammar.count("::="),
        }


def build_example_request(
    prompt: str,
    resources: OutputResources,
    *,
    key: str,
    title: str,
) -> ExampleRequest:
    """Bundle a prompt with the grammar and schema from the same resources."""
    return ExampleRequest(
        prompt=prompt,
        grammar=resources.gbnf,
        schema=resources.json_schema(key=key, title=title),
    )


def assert_response_matches_request(request: ExampleRequest, text: str) -> None:
    """Ensure a sample response matches the bundled constraint resources."""
    key = next(iter(request.schema["properties"]))
    pattern = request.schema["properties"][key]["pattern"]

    # The schema pattern is derived from the same limits as the bundled grammar.
    if re.fullmatch(pattern, text) is None:
        raise AssertionError(
            "Sample response does not match the bundled prompt-and-grammar constraints."
        )
