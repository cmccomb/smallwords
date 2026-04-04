from __future__ import annotations

from .types import WordlistSpec

# These are starter/demo lists meant to make the package usable immediately.
# Swap in fuller source-backed lists (e.g., Ogden, NGSL, CEFR-aligned lists)
# once you decide what you want to treat as canonical.

COMMON_50_WORDS = (
    "a", "about", "all", "and", "as", "at", "be", "big", "but", "by",
    "can", "come", "day", "do", "for", "from", "get", "go", "good", "have",
    "he", "help", "how", "i", "if", "in", "is", "it", "know", "like",
    "look", "make", "man", "more", "new", "not", "now", "of", "on", "one",
    "or", "say", "see", "small", "that", "the", "this", "to", "use", "with",
)

COMMON_100_WORDS = COMMON_50_WORDS + (
    "after", "again", "air", "an", "ask", "back", "because", "before", "best", "boy",
    "call", "change", "child", "come", "down", "end", "even", "every", "fact", "feel",
    "find", "first", "food", "give", "great", "hand", "high", "home", "just", "keep",
    "kind", "last", "leave", "life", "little", "long", "many", "may", "most", "move",
    "need", "next", "old", "only", "other", "our", "out", "over", "part", "people",
)

COMMON_250_WORDS = tuple(dict.fromkeys(COMMON_100_WORDS + (
    "answer", "around", "away", "bad", "become", "begin", "body", "book", "both", "build",
    "care", "carry", "cause", "city", "clear", "close", "cut", "each", "earth", "easy",
    "eat", "enough", "example", "eye", "face", "family", "far", "few", "fire", "follow",
    "form", "friend", "full", "game", "group", "grow", "hard", "head", "hear", "hold",
    "house", "idea", "important", "inside", "job", "keep", "kid", "learn", "light", "line",
    "live", "lot", "mean", "mind", "money", "month", "morning", "mother", "name", "night",
    "open", "place", "plan", "play", "point", "power", "put", "question", "read", "real",
    "reason", "right", "run", "same", "school", "set", "show", "side", "since", "stand",
    "start", "state", "stop", "story", "study", "system", "take", "tell", "thing", "think",
    "time", "try", "turn", "under", "want", "way", "week", "well", "while", "work",
    "world", "write", "year",
)))

SIMPLE_REASONING_WORDS = tuple(dict.fromkeys(COMMON_250_WORDS + (
    "step", "steps", "why", "then", "so", "result", "final", "note", "check", "list",
)))

COMMON_50_SPEC = WordlistSpec(
    name="common_50",
    words=COMMON_50_WORDS,
    description="Tiny starter list for demos and tests.",
)

COMMON_100_SPEC = WordlistSpec(
    name="common_100",
    words=COMMON_100_WORDS,
    description="Slightly richer starter list for small-word experiments.",
)

COMMON_250_SPEC = WordlistSpec(
    name="common_250",
    words=COMMON_250_WORDS,
    description="Starter list with enough coverage for short explanations.",
)

REASONING_250_SPEC = WordlistSpec(
    name="reasoning_250",
    words=SIMPLE_REASONING_WORDS,
    description="Starter list tuned for short visible planning blocks.",
    line_prefixes=("- ", "1. ", "2. ", "3. "),
)

WORDLISTS: dict[str, WordlistSpec] = {
    COMMON_50_SPEC.name: COMMON_50_SPEC,
    COMMON_100_SPEC.name: COMMON_100_SPEC,
    COMMON_250_SPEC.name: COMMON_250_SPEC,
    REASONING_250_SPEC.name: REASONING_250_SPEC,
}


def get_wordlist(name: str) -> WordlistSpec:
    try:
        return WORDLISTS[name]
    except KeyError as exc:
        raise KeyError(f"Unknown wordlist: {name!r}. Available: {sorted(WORDLISTS)}") from exc
