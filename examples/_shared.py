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
    """Bundle the prompt and constraint resources a runtime would use together.

    Attributes:
        prompt: Prompt text that should be sent to the model.
        grammar: GBNF grammar string that constrains the response.
        schema: JSON Schema object aligned with the same response limits.
    """

    prompt: str
    grammar: str
    schema: dict[str, Any]

    def summary(self) -> dict[str, Any]:
        """Return a compact summary of the bundled prompt-and-grammar request.

        Returns:
            A small dictionary with the most relevant request metadata.
        """
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
    """Bundle a prompt with the grammar and schema from the same resources.

    Args:
        prompt: Prompt text that should be sent to the model.
        resources: Output resources that define the grammar and schema.
        key: Property name for the generated single-key object schema.
        title: Schema title for the generated single-key object schema.

    Returns:
        A request bundle that keeps the prompt and constraints together.
    """
    return ExampleRequest(
        prompt=prompt,
        grammar=resources.gbnf,
        schema=resources.json_schema(key=key, title=title),
    )


def response_matches_request(request: ExampleRequest, text: str) -> bool:
    """Return True when a response matches the bundled constraint resources.

    Args:
        request: Prompt-plus-constraint bundle to validate against.
        text: Response text to validate.

    Returns:
        True when the response matches the bundled schema pattern.
    """
    key = next(iter(request.schema["properties"]))
    pattern = request.schema["properties"][key]["pattern"]

    # The schema pattern is derived from the same limits as the bundled grammar.
    return re.fullmatch(pattern, text) is not None
