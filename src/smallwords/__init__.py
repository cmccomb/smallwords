"""Expose the small public root API for ``smallwords``."""

from importlib.metadata import PackageNotFoundError, version

from .input_words import allow_input_words
from .remix import remix_wordlist
from .resources import OutputResources
from .types import OutputShape, WordFamily, WordlistSpec
from .validation import (
    OutputValidation,
    is_compliant,
    is_in_vocabulary,
    out_of_vocab,
    validate_output,
)
from .wordlists import get_wordlist, list_wordlists

try:
    __version__ = version("smallwords")
except PackageNotFoundError:
    __version__ = "0+unknown"

__all__ = [
    "OutputResources",
    "OutputShape",
    "OutputValidation",
    "WordFamily",
    "WordlistSpec",
    "__version__",
    "allow_input_words",
    "get_wordlist",
    "is_compliant",
    "is_in_vocabulary",
    "list_wordlists",
    "out_of_vocab",
    "remix_wordlist",
    "validate_output",
]
