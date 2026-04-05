"""Expand canonical vocabularies into conservative surface-form families.

This module is where the package's “simple English, but not painfully literal”
behavior lives. It keeps the automatic expansion logic centralized so prompts,
grammars, schemas, and validators all agree about which inflected forms are
allowed for a given vocabulary.
"""

from __future__ import annotations

from .types import WordFamily, WordlistSpec

# This map covers the common irregular verb families allowed by default.
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

# This map covers the irregular noun plurals allowed by default.
_IRREGULAR_NOUNS: dict[str, tuple[str, ...]] = {
    "child": ("children",),
    "foot": ("feet",),
    "man": ("men",),
    "mouse": ("mice",),
    "person": ("people",),
    "tooth": ("teeth",),
    "woman": ("women",),
}

# These regular verbs get conservative automatic inflection support.
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

# These regular nouns get conservative plural support.
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

# These verbs double the final consonant in the derived regular forms.
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

# These words should never receive automatic noun-style pluralization.
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
    """Lowercase, trim, and sort words for deterministic output resources.

    Args:
        words: Candidate words to normalize.

    Returns:
        The normalized words in stable sorted order.
    """
    # Deterministic ordering makes generated grammars, schemas, and diffs stable.
    return tuple(sorted({word.strip().lower() for word in words if word.strip()}))


def _plural_like(word: str) -> str:
    """Build a conservative plural or third-person-singular form.

    Args:
        word: Canonical base word to inflect.

    Returns:
        A conservative plural-like or third-person-singular form.
    """
    if word.endswith(("s", "sh", "ch", "x", "z", "o")):
        return word + "es"
    if len(word) > 1 and word.endswith("y") and word[-2] not in "aeiou":
        return word[:-1] + "ies"
    return word + "s"


def _gerund(word: str) -> str:
    """Build a regular English ``-ing`` form without broad doubling heuristics.

    Args:
        word: Canonical base word to inflect.

    Returns:
        The regular gerund form for the supplied word.
    """
    if word in _DOUBLE_FINAL_CONSONANT_VERBS:
        return word + word[-1] + "ing"
    if len(word) > 2 and word.endswith("ie"):
        return word[:-2] + "ying"
    if len(word) > 2 and word.endswith("e") and not word.endswith(("ee", "ye")):
        return word[:-1] + "ing"
    return word + "ing"


def _past(word: str) -> str:
    """Build a regular English past-tense or participle form.

    Args:
        word: Canonical base word to inflect.

    Returns:
        The regular past-tense or participle form for the supplied word.
    """
    if word in _DOUBLE_FINAL_CONSONANT_VERBS:
        return word + word[-1] + "ed"
    if len(word) > 1 and word.endswith("y") and word[-2] not in "aeiou":
        return word[:-1] + "ied"
    if word.endswith("e"):
        return word + "d"
    return word + "ed"


def _regular_noun_forms(word: str) -> set[str]:
    """Generate safe noun-style variants for a canonical headword.

    Args:
        word: Canonical base word to inflect.

    Returns:
        Conservative noun-style variants for the supplied word.
    """
    if word in _NON_INFLECTING_WORDS or len(word) < 2:
        return set()
    # Noun plurals are the broadest useful expansion and keep `city -> cities`.
    return {_plural_like(word)}


def _regular_verb_forms(word: str) -> set[str]:
    """Generate regular verb variants for curated base verbs only.

    Args:
        word: Canonical base word to inflect.

    Returns:
        Conservative regular verb variants for the supplied word.
    """
    return {_plural_like(word), _gerund(word), _past(word)}


def _family_forms(family: WordFamily) -> set[str]:
    """Expand one explicit family annotation into allowed surface forms.

    Args:
        family: Explicit word-family metadata to expand.

    Returns:
        The allowed surface forms implied by the family annotation.
    """
    word = family.headword.strip().lower()
    forms = {word, *(form.strip().lower() for form in family.forms if form.strip())}

    if family.kind == "noun":
        forms.update(_regular_noun_forms(word))
    elif family.kind == "verb":
        forms.update(_regular_verb_forms(word))

    return forms


def _auto_forms(word: str, *, variant_mode: str) -> set[str]:
    """Generate built-in English family forms for one canonical word.

    Args:
        word: Canonical base word to expand.
        variant_mode: Variant expansion mode to apply.

    Returns:
        The automatically generated surface forms for the supplied word.
    """
    if variant_mode != "english_inflections":
        return {word}

    forms = {word}
    # Irregular families win first because they are more precise than generic heuristics.
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
    """Expand a spec's canonical words into the surface forms callers may emit.

    Args:
        spec: Wordlist specification that defines the allowed tokens.

    Returns:
        The full allowed surface-form set for the supplied specification.
    """
    families = {
        family.headword.strip().lower(): family for family in spec.word_families
    }
    blocked = {word.strip().lower() for word in spec.blocked_forms if word.strip()}

    allowed: set[str] = set()
    for word in spec.canonical_words():
        # The canonical list remains the provenance source of truth for the spec.
        allowed.update(_auto_forms(word, variant_mode=spec.variant_mode))
        if word in families:
            # Explicit family data layers on top of the automatic expansion rules.
            allowed.update(_family_forms(families[word]))

    for family in families.values():
        # Families can inject headwords that were not listed literally in `words`.
        allowed.update(_family_forms(family))

    # Blocked forms are applied last so themed remixes can veto awkward expansions.
    allowed.difference_update(blocked)
    return _normalize(allowed)
