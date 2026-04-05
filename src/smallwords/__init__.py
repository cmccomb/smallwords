"""Expose the small, stable public API for ``smallwords``.

This module deliberately re-exports only the high-level helpers that a caller
is most likely to need from the package root. Lower-level builder functions and
internal utilities stay in their home modules so the root namespace remains
predictable for people, editors, and future AI agents.
"""

from importlib.metadata import PackageNotFoundError, version

# Re-export the small, high-level entry points so callers can stay on the package root.
from .input_words import allow_input_words
from .prompts import (
    prompt_answer_simply,
    prompt_explain_simply,
    prompt_rewrite_simply,
    prompt_summarize_simply,
)
from .remix import remix_wordlist
from .resources import (
    BASIC_850,
    CAVEMAN_898,
    MOBY_898,
    PIRATE_898,
    SPECIAL_ENGLISH_1475,
    OutputResources,
    make_gbnf,
    make_json_schema,
    make_resources,
)
from .types import WordFamily, WordlistSpec
from .validation import is_compliant, out_of_vocab
from .wordlists import get_wordlist, list_wordlists

# Re-export the installed package version for lightweight diagnostics and UIs.
try:
    __version__ = version("smallwords")
except PackageNotFoundError:
    # Source-tree imports can happen before packaging metadata has been installed.
    __version__ = "0+unknown"

# Keep low-level builders off the package root so the top-level API stays clean.
# Keep the export list explicit so generated docs and editors stay predictable.
__all__ = [
    "BASIC_850",
    "CAVEMAN_898",
    "MOBY_898",
    "OutputResources",
    "PIRATE_898",
    "SPECIAL_ENGLISH_1475",
    "__version__",
    "WordFamily",
    "WordlistSpec",
    "allow_input_words",
    "get_wordlist",
    "list_wordlists",
    "make_gbnf",
    "make_json_schema",
    "make_resources",
    "prompt_answer_simply",
    "prompt_explain_simply",
    "prompt_rewrite_simply",
    "prompt_summarize_simply",
    "remix_wordlist",
    "is_compliant",
    "out_of_vocab",
]
