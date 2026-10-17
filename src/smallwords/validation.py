"""Check vocabulary membership and validate the complete output contract.

The vocabulary helpers intentionally use a simple token-based view of text.
``validate_output`` additionally checks the output shape shared by GBNF and
JSON Schema resources.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from ._constraints import compile_constraints
from ._spec_utils import resolve_wordlist_spec
from .types import OutputShape, WordlistSpec


@dataclass(frozen=True)
class OutputValidation:
    """Report whether text matches the configured output contract.

    Attributes:
        valid: Whether the full vocabulary and output shape match.
        out_of_vocab: Best-effort word diagnostics for invalid output, excluding
            valid wrapper labels such as ``PLAN:`` and ``FINAL:``.
        issues: Human-readable reasons for an invalid response.
    """

    valid: bool
    out_of_vocab: tuple[str, ...]
    issues: tuple[str, ...]


def normalize_tokens(text: str) -> list[str]:
    """Extract lowercase Unicode letter runs from free-form text.

    Combining marks stay with their letters, and an apostrophe between letters
    stays within a token. This is delimiter-based extraction, not language-aware
    segmentation or Unicode normalization.

    Args:
        text: Free-form text to tokenize.

    Returns:
        The lowercase word tokens found in the input text.
    """
    tokens: list[str] = []
    current: list[str] = []

    def flush() -> None:
        if current:
            tokens.append("".join(current).lower())
            current.clear()

    for index, char in enumerate(text):
        category = unicodedata.category(char)[0]
        if (
            category == "L"
            or (category == "M" and current)
            or (
                char in ("'", "’")
                and current
                and index + 1 < len(text)
                and unicodedata.category(text[index + 1])[0] == "L"
            )
        ):
            current.append(char)
        else:
            flush()
    flush()
    return tokens


def out_of_vocab(text: str, wordlist: str | WordlistSpec) -> list[str]:
    """Return sorted unique tokens that are missing from the selected word list.

    Args:
        text: Free-form text to validate.
        wordlist: Built-in wordlist name or inline wordlist specification.

    Returns:
        Sorted unique tokens that are not permitted by the selected wordlist.
    """
    spec = resolve_wordlist_spec(wordlist)
    # Membership checks happen against the normalized set so punctuation and
    # capitalization never create false negatives.
    allowed = set(spec.allowed_words())
    # A set comprehension keeps duplicates out of the report while staying deterministic.
    return sorted({token for token in normalize_tokens(text) if token not in allowed})


def is_in_vocabulary(text: str, wordlist: str | WordlistSpec) -> bool:
    """Return True when every alphabetic token is in the selected word list.

    Args:
        text: Free-form text to validate.
        wordlist: Built-in wordlist name or inline wordlist specification.

    Returns:
        True when every normalized alphabetic token is permitted. This does not
        check numbers, punctuation, capitalization, or output shape.
    """
    return not out_of_vocab(text, wordlist)


def is_compliant(text: str, wordlist: str | WordlistSpec) -> bool:
    """Check vocabulary membership using the original public API.

    This compatibility helper checks words only. Use ``validate_output`` when
    punctuation, capitalization, wrappers, and line limits must also match.
    """
    return is_in_vocabulary(text, wordlist)


def _body_text(text: str, wrapper_labels: tuple[str, ...]) -> str:
    """Exclude valid response labels from vocabulary diagnostics."""
    if not wrapper_labels:
        return text
    first, second = wrapper_labels
    start = first + "\n"
    separator = "\n\n" + second + "\n"
    if text.startswith(start) and separator in text:
        before, after = text[len(start) :].split(separator, 1)
        return before + "\n" + after
    return text


def validate_output(
    text: str,
    wordlist: str | WordlistSpec,
    *,
    shape: OutputShape | None = None,
) -> OutputValidation:
    """Check text against the same vocabulary and shape as output resources.

    Args:
        text: Generated response text, without the surrounding JSON object.
        wordlist: Built-in wordlist name or inline specification.
        shape: Output shape used to build the GBNF or JSON Schema. The default
            matches ``OutputResources.from_wordlist``.

    Returns:
        A result with the full-contract verdict and diagnostic issues.
    """
    spec = resolve_wordlist_spec(wordlist)
    constraints = compile_constraints(spec, shape or OutputShape())
    body = _body_text(text, constraints.wrapper_labels)
    valid = re.fullmatch(constraints.response_pattern, text) is not None
    # A full-contract match proves that every emitted literal was permitted,
    # even if diagnostic tokenization would split a caller's unusual literal.
    missing = () if valid else tuple(out_of_vocab(body, spec))

    issues: list[str] = []
    if missing:
        issues.append("Out-of-vocabulary words: " + ", ".join(missing))
    if not valid:
        issues.append("Text does not match the configured vocabulary and output shape")

    return OutputValidation(valid=valid, out_of_vocab=missing, issues=tuple(issues))
