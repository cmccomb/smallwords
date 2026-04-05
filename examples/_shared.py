"""Shared helpers for the live llama.cpp examples."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "http://127.0.0.1:8080"
BASE_URL_ENV_VAR = "SMALLWORDS_LLAMA_BASE_URL"
REQUEST_TIMEOUT_SECONDS = 300.0


def server_base_url() -> str:
    """Return the llama-server base URL that examples should use."""
    return os.environ.get(BASE_URL_ENV_VAR, DEFAULT_BASE_URL).rstrip("/")


def request_completion(base_url: str, payload: dict[str, object]) -> dict[str, object]:
    """Send one chat-completion request to llama.cpp and decode the JSON response."""
    request = urllib.request.Request(
        f"{base_url}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(
            request, timeout=REQUEST_TIMEOUT_SECONDS
        ) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"llama-server returned HTTP {exc.code} for /v1/chat/completions: {detail}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Could not reach llama-server at {base_url}. "
            f"Start one locally or set {BASE_URL_ENV_VAR}. "
            f"Original error: {exc}"
        ) from exc


def generate_text(
    base_url: str,
    prompt: str,
    *,
    grammar: str | None = None,
    max_tokens: int,
    temperature: float,
    seed: int,
) -> str:
    """Run one prompt through llama.cpp and return the generated text."""
    payload: dict[str, object] = {
        "model": "unused",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "seed": seed,
    }
    if grammar is not None:
        payload["grammar"] = grammar

    response = request_completion(base_url, payload)
    return str(response["choices"][0]["message"]["content"]).strip()
