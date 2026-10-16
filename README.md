# smallwords

[![CI](https://github.com/cmccomb/smallwords/actions/workflows/ci.yml/badge.svg)](https://github.com/cmccomb/smallwords/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/smallwords)](https://pypi.org/project/smallwords/)
[![Python versions](https://img.shields.io/pypi/pyversions/smallwords)](https://pypi.org/project/smallwords/)
[![License](https://img.shields.io/github/license/cmccomb/smallwords)](https://github.com/cmccomb/smallwords/blob/main/LICENSE)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-4c1)](https://cmccomb.github.io/smallwords/)

`smallwords` is a tiny Python package for controlled-vocabulary prompting plus
portable output resources. It keeps one wordlist at the center of the workflow
so prompt text, GBNF, JSON Schema, and post-generation validation all stay in
sync.

The package ships with a small set of bundled wordlists: direct source-backed
lists such as `moby_898`, `basic_850`, and `special_english_1475`, plus three
intentionally themed remixes. Most built-ins also allow slight family variants
such as `go`, `goes`, and `going`; Caveman uses only its listed forms.

It supports Python 3.10 and newer.

The hosted API-and-examples docs live at
[`cmccomb.github.io/smallwords`](https://cmccomb.github.io/smallwords/).

## Installation

```bash
pip install smallwords
```

For local development, create and activate a virtualenv first:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Quick Start

```python
from smallwords import OutputResources, OutputShape, allow_input_words
from smallwords.prompts import build_prompt

shape = OutputShape(max_words_per_line=24, max_lines=1)
spec = allow_input_words("basic_850", "bridge")
resources = OutputResources.from_wordlist(spec, shape=shape)
prompt = build_prompt("explain", "How does a bridge work?", wordlist=spec)
schema = resources.json_schema(key="answer", title="bridge_explanation")

text = "A bridge is a structure that helps people and things move across a river or a deep place."
result = resources.validate(text)
assert result.valid, result.issues
```

The contrast is the point. `build_prompt(...)` is the soft instruction layer.
`OutputResources` gives you the matching hard constraints in both GBNF and JSON
Schema form. `resources.validate(...)` checks a response against the same
vocabulary and output shape. The older `is_compliant(...)` helper remains a
vocabulary-only check; it does not check punctuation or output shape.

Run the complete offline example without a model server:

```bash
python examples/offline_quickstart.py
```

If you want the model to be able to repeat an essential topic term such as
`bridge`, pass just that term to `allow_input_words(...)`. Passing an entire
technical passage will also allow every technical word in it.

## Built-In Wordlists

- `moby_898`: the full normalized alpha-only Moby Words II frequency list
- `basic_850`: Charles Ogden's Basic English 850
- `special_english_1475`: Voice of America Special English
- `caveman_898`: a 348-word, surface-only `moby_898` remix with short Germanic-rooted words
- `cowboy_898`: a size-neutral `moby_898` remix for ranch and trail stories
- `pirate_898`: a size-neutral `moby_898` remix for playful sea stories

The bundled text files live in `src/smallwords/data/`. `moby_898`,
`basic_850`, and `special_english_1475` are direct source-backed lists.
`caveman_898`, `cowboy_898`, and `pirate_898` are derived from `moby_898`.

The caveman preset now keeps 348 one-syllable words with Germanic roots, such
as `bone`, `stone`, `spear`, `ash`, and `wolf`. It drops obvious Latin, Greek,
and French borrowings, as well as words with unclear roots. Its public name
still ends in `898` because it starts from `moby_898`; it no longer has 898
entries. The [full removal list](docs/caveman_removed_words.txt) records all
551 words removed from the former preset and the added word `gap`. The
[curated vocabulary](src/smallwords/data/caveman_germanic_monosyllables.txt)
is the source of truth. Pronunciations were screened with
[CMUdict](https://github.com/cmusphinx/cmudict), and word origins with a
[Wiktionary-derived classification](https://github.com/cavedave/EnglishWords)
and [Wiktionary](https://en.wiktionary.org/wiki/Help:Etymology) spot checks.
Etymologies can be disputed, so this is a deliberately conservative voice
preset.

The cowboy and pirate presets each swap 40 abstract base words for themed terms
and everyday pronouns missing from `moby_898`. Their `style_hint` values guide
`build_prompt(...)`; the generated grammar and schema still enforce the
vocabulary and output shape. These are playful voices, not historical dialect
models. The terms draw on [National Park Service cowboy history](https://www.nps.gov/tapr/learn/historyculture/cowboys.htm)
and [Royal Museums Greenwich's pirate word guide](https://www.rmg.co.uk/press-release/international-talk-pirate-weekend).

Run `python examples/themed_presets.py` to inspect both prompts and validate
sample lines without a model server. The remixes live in
`src/smallwords/themes/`. Use `remix_wordlist(...)` to build your own.

## Contrastive Example

This paired example starts with the opening sentence and a compressed later
line from the familiar [missile-guidance monologue](https://www.reddit.com/r/copypasta/comments/p1us5i/the_missile_knows_where_it_is_at_all_times/),
then asks for six controlled-vocabulary versions.
The six rewrites below are unedited local model outputs from October 15,
2026. The runs used
`ibm-granite/granite-4.2-8b-GGUF` through `llama-server` from
`llama.cpp`.

Each rewrite used generated GBNF from a task-focused subset of the named
preset. The Simple run adds only `missile`, which now appears in the source
passage, because `moby_898` does not contain it. Every constrained result also
passes the same output-shape check against its full validation wordlist.

| Mode | Model output | Full-wordlist validation |
| --- | --- | --- |
| Original | “The missile knows where it is at all times. By subtracting where it is from where it isn't, or where it isn't from where it is, it obtains a difference, or deviation.” | Source text |
| Simple (`moby_898` + `missile`) | “The missile knows where it is at all times.<br>It knows where it should be next.<br>The difference tells it how far to move.” | Passes |
| Caveman (`caveman_898`) | “Stone know where it be now.<br>Stone know where it should be.<br>Gap tell stone how far to go.” | Passes |
| Basic English (`basic_850`) | “The thing has knowledge of where the thing is now.<br>The thing is to be at the other place.<br>The distance from here to there is how far to move.” | Passes |
| Special English (`special_english_1475`) | “The missile knows where it is at all times.<br>It should be at the second place.<br>The distance tells how far to move from here to there.” | Passes |
| Pirate (`pirate_898`) | “The ship knows where it is now.<br>The crew knows where the ship should be.<br>The difference tells the crew which way to sail.” | Passes |
| Cowboy (`cowboy_898`) | “The cowboy knows where the cattle are now.<br>The ranch is where the cattle should be.<br>The difference tells the cowboy which way to ride.” | Passes |

The focused subsets keep the generated grammar compact for a specific task;
they add no words outside the underlying presets except the explicit `missile`
allowance in Simple. The themed prompts use a stone, ship, or cattle as an
analogy. Each rewrite now says who knows the current place, then explains the
target place and the difference between them.

## Examples

Start with the offline quick start above. For live-model examples, see the repository's
[`examples/README.md`](https://github.com/cmccomb/smallwords/blob/main/examples/README.md)
for the runnable examples. The missile contrast, pirate greeting, and technical
rewrite call a live `llama-server` model with a prompt plus generated grammar.

## Development

Run these commands from an activated virtualenv:

```bash
python -m pip install -e ".[dev]"
python -m ruff check .
python -m ruff format --check .
python -m pytest
python scripts/check_documentation.py
python -m sphinx -W --keep-going -b html docs docs/_build/html
python -m build
python -m twine check --strict dist/*
```

CI runs linting, tests, the documentation policy check, a `>=90%` coverage
gate, a Sphinx docs build, and a package build on GitHub Actions.

For release steps and Trusted Publishing setup, see
[`RELEASING.md`](https://github.com/cmccomb/smallwords/blob/main/RELEASING.md).
