from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Any

from .grammar_builder import ThinkingMode, build_gbnf
from .types import WordlistSpec
from .wordlists import COMMON_50_SPEC, COMMON_100_SPEC, COMMON_250_SPEC, REASONING_250_SPEC, get_wordlist


@dataclass(frozen=True)
class PrebuiltGrammar:
    spec: WordlistSpec
    thinking_mode: ThinkingMode = "none"
    max_words_per_line: int = 40
    max_lines: int = 8

    @cached_property
    def gbnf(self) -> str:
        return build_gbnf(
            self.spec,
            thinking_mode=self.thinking_mode,
            max_words_per_line=self.max_words_per_line,
            max_lines=self.max_lines,
        )

    def to_llama_grammar(self) -> Any:
        try:
            from llama_cpp import LlamaGrammar
        except ImportError as exc:
            raise ImportError(
                "llama-cpp-python is not installed. Install with: pip install smallwords[llama-cpp]"
            ) from exc
        return LlamaGrammar.from_string(self.gbnf)

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(self.gbnf)


COMMON_50 = PrebuiltGrammar(COMMON_50_SPEC)
COMMON_100 = PrebuiltGrammar(COMMON_100_SPEC)
COMMON_250 = PrebuiltGrammar(COMMON_250_SPEC)

COMMON_50_THINKING = PrebuiltGrammar(REASONING_250_SPEC, thinking_mode="plan_final")
COMMON_100_THINKING = PrebuiltGrammar(REASONING_250_SPEC, thinking_mode="plan_final")
COMMON_250_THINKING = PrebuiltGrammar(REASONING_250_SPEC, thinking_mode="thinking_answer")


def make_grammar(
    wordlist: str | WordlistSpec,
    *,
    thinking_mode: ThinkingMode = "none",
    max_words_per_line: int = 40,
    max_lines: int = 8,
) -> PrebuiltGrammar:
    spec = get_wordlist(wordlist) if isinstance(wordlist, str) else wordlist
    return PrebuiltGrammar(
        spec=spec,
        thinking_mode=thinking_mode,
        max_words_per_line=max_words_per_line,
        max_lines=max_lines,
    )
