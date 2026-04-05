"""Public package exports for the smallwords API."""

# Re-export the common entry points so callers can stay on the package root.
from .grammar_builder import build_gbnf
from .json_schema import build_json_schema
from .prompts import (
    TEMPLATE_PROMPTS,
    prompt_answer_simply,
    prompt_explain_simply,
    prompt_rewrite_simply,
    prompt_summarize_simply,
)
from .remix import remix_wordlist
from .resources import (
    BASIC_850,
    CAVEMAN_250,
    COMMON_50,
    COMMON_50_THINKING,
    COMMON_100,
    COMMON_100_THINKING,
    COMMON_250,
    COMMON_250_THINKING,
    PIRATE_250,
    REASONING_250,
    SPECIAL_ENGLISH,
    OutputResources,
    make_json_schema,
    make_resources,
)
from .types import WordFamily, WordlistSpec
from .validation import is_compliant, out_of_vocab
from .wordlists import WORDLISTS, get_wordlist

# Keep the export list explicit so generated docs and editors stay predictable.
__all__ = [
    "BASIC_850",
    "CAVEMAN_250",
    "COMMON_50",
    "COMMON_50_THINKING",
    "COMMON_100",
    "COMMON_100_THINKING",
    "COMMON_250",
    "COMMON_250_THINKING",
    "OutputResources",
    "PIRATE_250",
    "REASONING_250",
    "SPECIAL_ENGLISH",
    "WordFamily",
    "WordlistSpec",
    "WORDLISTS",
    "build_gbnf",
    "build_json_schema",
    "get_wordlist",
    "make_json_schema",
    "make_resources",
    "prompt_answer_simply",
    "prompt_explain_simply",
    "prompt_rewrite_simply",
    "prompt_summarize_simply",
    "remix_wordlist",
    "TEMPLATE_PROMPTS",
    "is_compliant",
    "out_of_vocab",
]
