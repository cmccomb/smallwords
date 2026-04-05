"""Word-family expansion helpers shared by validation, grammar, and schema."""

from __future__ import annotations

from .types import WordFamily, WordlistSpec

_IRREGULAR_FAMILIES: dict[str, tuple[str, ...]] = {
    "be": ("am", "is", "are", "was", "were", "being", "been"),
    "become": ("becomes", "becoming", "became"),
    "begin": ("begins", "beginning", "began", "begun"),
    "break": ("breaks", "breaking", "broke", "broken"),
    "bring": ("brings", "bringing", "brought"),
    "build": ("builds", "building", "built"),
    "buy": ("buys", "buying", "bought"),
    "choose": ("chooses", "choosing", "chose", "chosen"),
    "come": ("comes", "coming", "came"),
    "cut": ("cuts", "cutting"),
    "do": ("does", "doing", "did", "done"),
    "drink": ("drinks", "drinking", "drank", "drunk"),
    "drive": ("drives", "driving", "drove", "driven"),
    "eat": ("eats", "eating", "ate", "eaten"),
    "fall": ("falls", "falling", "fell", "fallen"),
    "feel": ("feels", "feeling", "felt"),
    "fight": ("fights", "fighting", "fought"),
    "find": ("finds", "finding", "found"),
    "fly": ("flies", "flying", "flew", "flown"),
    "get": ("gets", "getting", "got", "gotten"),
    "give": ("gives", "giving", "gave", "given"),
    "go": ("goes", "going", "went", "gone"),
    "grow": ("grows", "growing", "grew", "grown"),
    "have": ("has", "having", "had"),
    "hear": ("hears", "hearing", "heard"),
    "hold": ("holds", "holding", "held"),
    "keep": ("keeps", "keeping", "kept"),
    "know": ("knows", "knowing", "knew", "known"),
    "leave": ("leaves", "leaving", "left"),
    "lead": ("leads", "leading", "led"),
    "lose": ("loses", "losing", "lost"),
    "make": ("makes", "making", "made"),
    "mean": ("means", "meaning", "meant"),
    "meet": ("meets", "meeting", "met"),
    "pay": ("pays", "paying", "paid"),
    "plan": ("plans", "planning", "planned"),
    "put": ("puts", "putting"),
    "read": ("reads", "reading"),
    "rise": ("rises", "rising", "rose", "risen"),
    "run": ("runs", "running", "ran"),
    "say": ("says", "saying", "said"),
    "see": ("sees", "seeing", "saw", "seen"),
    "sell": ("sells", "selling", "sold"),
    "send": ("sends", "sending", "sent"),
    "set": ("sets", "setting"),
    "show": ("shows", "showing", "showed", "shown"),
    "sit": ("sits", "sitting", "sat"),
    "sleep": ("sleeps", "sleeping", "slept"),
    "speak": ("speaks", "speaking", "spoke", "spoken"),
    "stand": ("stands", "standing", "stood"),
    "take": ("takes", "taking", "took", "taken"),
    "teach": ("teaches", "teaching", "taught"),
    "tell": ("tells", "telling", "told"),
    "think": ("thinks", "thinking", "thought"),
    "win": ("wins", "winning", "won"),
    "write": ("writes", "writing", "wrote", "written"),
}

_IRREGULAR_NOUNS: dict[str, tuple[str, ...]] = {
    "child": ("children",),
    "foot": ("feet",),
    "man": ("men",),
    "mouse": ("mice",),
    "person": ("people",),
    "tooth": ("teeth",),
    "woman": ("women",),
}

_AUTO_VERB_BASES = {
    "accept",
    "act",
    "add",
    "agree",
    "answer",
    "appear",
    "argue",
    "arrive",
    "ask",
    "attack",
    "believe",
    "call",
    "change",
    "compare",
    "consider",
    "continue",
    "control",
    "cook",
    "create",
    "damage",
    "decide",
    "demand",
    "deny",
    "die",
    "end",
    "enjoy",
    "explain",
    "follow",
    "force",
    "forgive",
    "gain",
    "happen",
    "help",
    "hope",
    "improve",
    "include",
    "increase",
    "influence",
    "join",
    "jump",
    "kill",
    "learn",
    "like",
    "listen",
    "live",
    "look",
    "love",
    "move",
    "need",
    "offer",
    "open",
    "plan",
    "play",
    "pull",
    "push",
    "remain",
    "remember",
    "report",
    "require",
    "return",
    "seem",
    "serve",
    "start",
    "stay",
    "study",
    "talk",
    "travel",
    "try",
    "turn",
    "use",
    "wait",
    "walk",
    "want",
    "watch",
    "work",
}

_AUTO_NOUN_BASES = {
    "area",
    "body",
    "boy",
    "business",
    "car",
    "case",
    "child",
    "city",
    "company",
    "country",
    "day",
    "door",
    "face",
    "fact",
    "family",
    "field",
    "force",
    "form",
    "girl",
    "government",
    "group",
    "head",
    "home",
    "hour",
    "house",
    "kind",
    "law",
    "line",
    "member",
    "month",
    "name",
    "nation",
    "number",
    "office",
    "order",
    "part",
    "period",
    "place",
    "point",
    "power",
    "president",
    "problem",
    "program",
    "question",
    "reason",
    "result",
    "room",
    "school",
    "service",
    "side",
    "street",
    "system",
    "thing",
    "time",
    "value",
    "war",
    "water",
    "way",
    "week",
    "word",
    "world",
    "year",
}

_DOUBLE_FINAL_CONSONANT_VERBS = {
    "drop",
    "plan",
    "ship",
    "shop",
    "slip",
    "step",
    "stop",
    "trip",
}

_NON_INFLECTING_WORDS = {
    "a",
    "all",
    "also",
    "an",
    "and",
    "any",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "he",
    "i",
    "if",
    "in",
    "it",
    "may",
    "more",
    "most",
    "must",
    "no",
    "not",
    "of",
    "on",
    "or",
    "other",
    "our",
    "she",
    "so",
    "some",
    "than",
    "that",
    "the",
    "their",
    "them",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "to",
    "up",
    "us",
    "we",
    "what",
    "when",
    "which",
    "who",
    "with",
    "would",
    "you",
}


def _normalize(words: tuple[str, ...] | list[str] | set[str]) -> tuple[str, ...]:
    """Lowercase, trim, and sort words for deterministic output resources."""
    return tuple(sorted({word.strip().lower() for word in words if word.strip()}))


def _plural_like(word: str) -> str:
    """Build a conservative plural or third-person-singular form."""
    if word.endswith(("s", "sh", "ch", "x", "z", "o")):
        return word + "es"
    if len(word) > 1 and word.endswith("y") and word[-2] not in "aeiou":
        return word[:-1] + "ies"
    return word + "s"


def _gerund(word: str) -> str:
    """Build a regular English `-ing` form without broad doubling heuristics."""
    if word in _DOUBLE_FINAL_CONSONANT_VERBS:
        return word + word[-1] + "ing"
    if len(word) > 2 and word.endswith("ie"):
        return word[:-2] + "ying"
    if len(word) > 2 and word.endswith("e") and not word.endswith(("ee", "ye")):
        return word[:-1] + "ing"
    return word + "ing"


def _past(word: str) -> str:
    """Build a regular English past-tense or participle form."""
    if word in _DOUBLE_FINAL_CONSONANT_VERBS:
        return word + word[-1] + "ed"
    if len(word) > 1 and word.endswith("y") and word[-2] not in "aeiou":
        return word[:-1] + "ied"
    if word.endswith("e"):
        return word + "d"
    return word + "ed"


def _regular_noun_forms(word: str) -> set[str]:
    """Generate safe noun-style variants for a canonical headword."""
    if word in _NON_INFLECTING_WORDS or len(word) < 2:
        return set()
    # Noun plurals are the broadest useful expansion and keep `city -> cities`.
    return {_plural_like(word)}


def _regular_verb_forms(word: str) -> set[str]:
    """Generate regular verb variants for curated base verbs only."""
    return {_plural_like(word), _gerund(word), _past(word)}


def _family_forms(family: WordFamily) -> set[str]:
    """Expand one explicit family annotation into allowed surface forms."""
    word = family.headword.strip().lower()
    forms = {word, *(form.strip().lower() for form in family.forms if form.strip())}

    if family.kind == "noun":
        forms.update(_regular_noun_forms(word))
    elif family.kind == "verb":
        forms.update(_regular_verb_forms(word))

    return forms


def _auto_forms(word: str, *, variant_mode: str) -> set[str]:
    """Generate built-in English family forms for one canonical word."""
    if variant_mode != "english_inflections":
        return {word}

    forms = {word}
    if word in _IRREGULAR_FAMILIES:
        forms.update(_IRREGULAR_FAMILIES[word])
    elif word in _AUTO_VERB_BASES:
        forms.update(_regular_verb_forms(word))

    if word in _IRREGULAR_NOUNS:
        forms.update(_IRREGULAR_NOUNS[word])
    elif word in _AUTO_NOUN_BASES:
        forms.update(_regular_noun_forms(word))

    return forms


def expand_allowed_words(spec: WordlistSpec) -> tuple[str, ...]:
    """Expand a spec's canonical words into the surface forms callers may emit."""
    families = {
        family.headword.strip().lower(): family for family in spec.word_families
    }
    blocked = {word.strip().lower() for word in spec.blocked_forms if word.strip()}

    allowed: set[str] = set()
    for word in spec.canonical_words():
        # The canonical list remains the provenance source of truth for the spec.
        allowed.update(_auto_forms(word, variant_mode=spec.variant_mode))
        if word in families:
            allowed.update(_family_forms(families[word]))

    for family in families.values():
        # Families can inject headwords that were not listed literally in `words`.
        allowed.update(_family_forms(family))

    allowed.difference_update(blocked)
    return _normalize(allowed)
