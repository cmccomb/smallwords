"""Target branchy coverage paths that matter for runtime behavior."""

from __future__ import annotations

import importlib
import importlib.metadata
import io
import json
import re
import urllib.error

import pytest

import smallwords
from smallwords.grammar_builder import build_gbnf
from smallwords.integrations import (
    generate_text,
    llama_server,
    request_completion,
    server_base_url,
)
from smallwords.json_schema import (
    _max_response_length,
    _max_text_length,
    _min_response_length,
    _min_text_length,
    _pattern_alt,
    _response_pattern,
    _word_pattern,
    build_json_schema,
)
from smallwords.themes import build_caveman_spec, build_pirate_spec
from smallwords.types import WordFamily, WordlistSpec
from smallwords.wordlists import get_wordlist


def test_package_version_falls_back_when_metadata_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure source-tree imports keep a safe fallback version string."""

    def _raise_package_not_found(_: str) -> str:
        """Raise the same error the import path handles during reload."""
        raise importlib.metadata.PackageNotFoundError

    monkeypatch.setattr(importlib.metadata, "version", _raise_package_not_found)
    reloaded = importlib.reload(smallwords)
    try:
        assert reloaded.__version__ == "0+unknown"
    finally:
        # Reload again after undoing the patch so later tests see the normal module state.
        monkeypatch.undo()
        importlib.reload(reloaded)


def test_build_gbnf_supports_prefixes_numbers_and_thinking_wrappers() -> None:
    """Ensure the grammar builder emits optional advanced rules when requested."""
    spec = WordlistSpec(
        name="bullet_count",
        words=("go",),
        allow_capitalized_words=False,
        allow_numbers=True,
        line_prefixes=("- ", "1. "),
    )

    grammar = build_gbnf(
        spec,
        thinking_mode="thinking_answer",
        min_words_per_line=2,
        max_words_per_line=2,
        max_lines=2,
    )
    plan_grammar = build_gbnf(
        spec,
        thinking_mode="plan_final",
        min_words_per_line=2,
        max_words_per_line=2,
        max_lines=2,
    )

    assert 'root ::= "THINKING:' in grammar
    assert 'root ::= "PLAN:' in plan_grammar
    assert "number ::= [0-9]+" in grammar
    assert 'line-prefix ::= "- " | "1. "' in grammar
    assert "line ::= line-prefix? word (space word){1,1} punct?" in grammar


def test_build_gbnf_rejects_invalid_settings() -> None:
    """Ensure the grammar builder fails fast on invalid limits and modes."""
    spec = WordlistSpec(name="tiny", words=("go",), variant_mode="surface_only")

    with pytest.raises(ValueError, match="min_words_per_line must be >= 1"):
        build_gbnf(spec, min_words_per_line=0)
    with pytest.raises(ValueError, match="max_words_per_line must be >= 1"):
        build_gbnf(spec, max_words_per_line=0)
    with pytest.raises(
        ValueError, match="min_words_per_line must be <= max_words_per_line"
    ):
        build_gbnf(spec, min_words_per_line=2, max_words_per_line=1)
    with pytest.raises(ValueError, match="max_lines must be >= 1"):
        build_gbnf(spec, max_lines=0)
    with pytest.raises(ValueError, match="Wordlist must contain at least one word"):
        build_gbnf(WordlistSpec(name="empty", words=()), max_words_per_line=1)
    with pytest.raises(ValueError, match="Unsupported thinking_mode"):
        build_gbnf(spec, thinking_mode="mystery")  # type: ignore[arg-type]


def test_json_schema_helpers_cover_singletons_and_error_paths() -> None:
    """Ensure the regex helpers handle edge cases and validation failures."""
    spec = WordlistSpec(name="tiny", words=("go",), allow_capitalized_words=False)

    assert _pattern_alt(["go"]) == "go"
    assert _min_text_length(spec, min_words_per_line=2, max_lines=1) == len("go go")
    with pytest.raises(ValueError, match="Wordlist must contain at least one word"):
        _word_pattern(WordlistSpec(name="empty", words=()))
    with pytest.raises(ValueError, match="Wordlist must contain at least one word"):
        _max_text_length(
            WordlistSpec(name="empty", words=()), max_words_per_line=1, max_lines=1
        )
    with pytest.raises(ValueError, match="key must be a non-empty string"):
        build_json_schema(spec, key="")
    with pytest.raises(ValueError, match="min_words_per_line must be >= 1"):
        build_json_schema(spec, min_words_per_line=0)
    with pytest.raises(ValueError, match="max_words_per_line must be >= 1"):
        build_json_schema(spec, max_words_per_line=0)
    with pytest.raises(
        ValueError, match="min_words_per_line must be <= max_words_per_line"
    ):
        build_json_schema(spec, min_words_per_line=2, max_words_per_line=1)
    with pytest.raises(ValueError, match="max_lines must be >= 1"):
        build_json_schema(spec, max_lines=0)


def test_json_schema_supports_thinking_answer_and_rejects_bad_modes() -> None:
    """Ensure schema helpers mirror both wrapper modes and mode validation."""
    spec = WordlistSpec(
        name="tiny",
        words=("go",),
        allow_capitalized_words=False,
        allow_newlines=False,
        allowed_punctuation=(),
        variant_mode="surface_only",
    )

    schema = build_json_schema(
        spec,
        thinking_mode="thinking_answer",
        max_words_per_line=1,
        max_lines=1,
    )
    pattern = schema["properties"]["text"]["pattern"]

    assert re.fullmatch(pattern, "THINKING:\ngo\n\nANSWER:\ngo")
    assert _min_response_length(
        spec,
        thinking_mode="thinking_answer",
        min_words_per_line=1,
        max_lines=1,
    ) == len("THINKING:\ngo\n\nANSWER:\ngo")
    assert _max_response_length(
        spec,
        thinking_mode="thinking_answer",
        max_words_per_line=1,
        max_lines=1,
    ) == len("THINKING:\ngo\n\nANSWER:\ngo")
    with pytest.raises(ValueError, match="Unsupported thinking_mode"):
        _response_pattern(
            spec,
            thinking_mode="mystery",  # type: ignore[arg-type]
            min_words_per_line=1,
            max_words_per_line=1,
            max_lines=1,
        )
    with pytest.raises(ValueError, match="Unsupported thinking_mode"):
        _max_response_length(
            spec,
            thinking_mode="mystery",  # type: ignore[arg-type]
            max_words_per_line=1,
            max_lines=1,
        )


def test_explicit_word_families_cover_regular_inflection_edges() -> None:
    """Ensure family metadata can drive conservative regular edge inflections."""
    spec = WordlistSpec(
        name="families",
        words=(),
        variant_mode="surface_only",
        word_families=(
            WordFamily("stop", kind="verb"),
            WordFamily("die", kind="verb"),
            WordFamily("a", kind="noun"),
            WordFamily("city", kind="noun"),
        ),
    )
    allowed = set(spec.allowed_words())

    assert {"stop", "stopped", "stopping"} <= allowed
    assert {"die", "dying"} <= allowed
    assert {"city", "cities"} <= allowed
    assert "as" not in allowed


def test_unknown_wordlist_error_lists_available_names() -> None:
    """Ensure lookup errors point users toward the valid built-in names."""
    with pytest.raises(KeyError, match="Available"):
        get_wordlist("definitely_not_real")


def test_llama_server_helpers_cover_success_and_error_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure the local llama.cpp helpers handle success and failure cases.

    Args:
        monkeypatch: Pytest monkeypatch fixture for replacing network calls.

    Returns:
        None.
    """

    class _FakeResponse:
        """Minimal context-manager response object for urlopen patches."""

        def __init__(self, payload: dict[str, object]) -> None:
            """Store one JSON payload for later reads.

            Args:
                payload: Response body that should be returned by ``read()``.
            """
            self._payload = payload

        def __enter__(self) -> _FakeResponse:
            """Enter the fake response context.

            Returns:
                The fake response itself.
            """
            return self

        def __exit__(self, *_: object) -> None:
            """Exit the fake response context.

            Returns:
                None.
            """

        def read(self) -> bytes:
            """Return the encoded JSON payload.

            Returns:
                JSON payload bytes for the fake response.
            """
            return json.dumps(self._payload).encode("utf-8")

    captured: dict[str, object] = {}

    def _urlopen_success(request: object, timeout: float) -> _FakeResponse:
        """Capture one request and return a successful chat-completion payload.

        Args:
            request: Request object passed to ``urlopen``.
            timeout: Timeout value forwarded by the helper.

        Returns:
            A fake response containing one assistant message.
        """
        captured["full_url"] = request.full_url
        captured["timeout"] = timeout
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        return _FakeResponse({"choices": [{"message": {"content": " Ahoy there! "}}]})

    monkeypatch.setenv(llama_server.BASE_URL_ENV_VAR, "http://example.test/root/")
    monkeypatch.setattr(llama_server.urllib.request, "urlopen", _urlopen_success)

    assert server_base_url() == "http://example.test/root"
    response = request_completion(
        "http://example.test/root",
        {"messages": [{"role": "user", "content": "hello"}]},
    )
    assert response["choices"][0]["message"]["content"] == " Ahoy there! "
    assert captured["full_url"] == "http://example.test/root/v1/chat/completions"
    assert captured["timeout"] == llama_server.REQUEST_TIMEOUT_SECONDS

    generated = generate_text(
        "http://example.test/root",
        "Say hello.",
        grammar='root ::= "hello"',
        max_tokens=7,
        temperature=0.2,
        seed=11,
    )
    assert generated == "Ahoy there!"
    assert captured["payload"] == {
        "model": "unused",
        "messages": [{"role": "user", "content": "Say hello."}],
        "max_tokens": 7,
        "temperature": 0.2,
        "seed": 11,
        "grammar": 'root ::= "hello"',
    }

    def _urlopen_http_error(*_: object, **__: object) -> _FakeResponse:
        """Raise an HTTP error with a readable response body.

        Returns:
            This helper never returns because it always raises.
        """
        raise urllib.error.HTTPError(
            "http://example.test/root/v1/chat/completions",
            500,
            "Server Error",
            hdrs=None,
            fp=io.BytesIO(b"problem detail"),
        )

    monkeypatch.setattr(llama_server.urllib.request, "urlopen", _urlopen_http_error)
    with pytest.raises(RuntimeError, match="HTTP 500"):
        request_completion("http://example.test/root", {"messages": []})

    def _urlopen_url_error(*_: object, **__: object) -> _FakeResponse:
        """Raise a URL error that mimics an unreachable local server.

        Returns:
            This helper never returns because it always raises.
        """
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(llama_server.urllib.request, "urlopen", _urlopen_url_error)
    with pytest.raises(RuntimeError, match="SMALLWORDS_LLAMA_BASE_URL"):
        request_completion("http://example.test/root", {"messages": []})


def test_themed_builders_reject_unbalanced_remixes() -> None:
    """Ensure themed remix builders fail if the base list cannot balance swaps."""
    tiny_base = WordlistSpec(name="tiny", words=("a",), variant_mode="surface_only")

    with pytest.raises(ValueError, match="caveman remix"):
        build_caveman_spec(tiny_base)
    with pytest.raises(ValueError, match="pirate remix"):
        build_pirate_spec(tiny_base)
