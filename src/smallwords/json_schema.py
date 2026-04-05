"""Serialize compiled constraints into JSON Schema."""

from __future__ import annotations

from typing import Any

from ._constraints import compile_constraints
from .types import OutputShape, WordlistSpec


def build_json_schema(
    spec: WordlistSpec,
    *,
    shape: OutputShape,
    key: str = "text",
    title: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Build a strict single-key JSON Schema aligned with the shared constraints."""
    if not key:
        raise ValueError("key must be a non-empty string")

    constraints = compile_constraints(spec, shape)
    value_schema: dict[str, Any] = {
        "type": "string",
        "pattern": constraints.response_pattern,
        "minLength": constraints.min_response_length,
        "description": description
        or f"Response text constrained to the {spec.name} word list.",
    }

    if constraints.max_response_length is not None:
        value_schema["maxLength"] = constraints.max_response_length

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": title or f"{spec.name}_response",
        "type": "object",
        "properties": {key: value_schema},
        "required": [key],
        "additionalProperties": False,
    }
