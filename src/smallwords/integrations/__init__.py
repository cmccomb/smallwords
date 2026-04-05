"""Optional runtime-specific helpers that are not re-exported from the package root.

The core public API stays runtime-agnostic, but lightweight helpers that are
useful for examples or local experiments can live here without cluttering the
top-level namespace.
"""

# This subpackage currently exposes a small helper for local llama.cpp servers.
from .llama_server import generate_text, request_completion, server_base_url

# Keep the subpackage surface explicit for readers and tooling.
__all__ = ["generate_text", "request_completion", "server_base_url"]
