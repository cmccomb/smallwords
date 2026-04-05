"""Internal helpers for talking to a running local llama.cpp server."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

# This default URL keeps the examples simple when llama-server is running locally.
DEFAULT_BASE_URL = "http://127.0.0.1:8080"
# This environment variable lets callers point the examples at another server.
BASE_URL_ENV_VAR = "SMALLWORDS_LLAMA_BASE_URL"
# This timeout covers a full local generation call.
REQUEST_TIMEOUT_SECONDS = 300.0


def server_base_url() -> str:
    """Return the llama-server base URL that examples should use.

    Returns:
        The configured llama-server base URL with any trailing slash removed.
    """
    return os.environ.get(BASE_URL_ENV_VAR, DEFAULT_BASE_URL).rstrip("/")


def request_completion(base_url: str, payload: dict[str, object]) -> dict[str, object]:
    """Send one chat-completion request to llama.cpp and decode the JSON response.

    Args:
        base_url: Base URL of the llama.cpp HTTP server.
        payload: Request body for the ``/v1/chat/completions`` endpoint.

    Returns:
        The decoded JSON response from llama.cpp.

    Raises:
        RuntimeError: If the server cannot be reached or returns an HTTP error.
    """
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
    """Run one prompt through llama.cpp and return the generated text.

    Args:
        base_url: Base URL of the llama.cpp HTTP server.
        prompt: Prompt text that should be sent to the model.
        grammar: Optional GBNF grammar string to constrain the response.
        max_tokens: Maximum tokens to generate.
        temperature: Sampling temperature for the generation run.
        seed: Deterministic seed for reproducible generation.

    Returns:
        The stripped generated answer text.
    """
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

    # The OpenAI-compatible chat response returns content inside the first message.
    return str(response["choices"][0]["message"]["content"]).strip()
