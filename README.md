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
intentionally themed remixes. By default, the built-ins also allow
slight family variants such as `go`, `goes`, and `going`.

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
- `caveman_898`: a size-neutral surface-only `moby_898` remix with caveman adjustments
- `cowboy_898`: a size-neutral `moby_898` remix for ranch and trail stories
- `pirate_898`: a size-neutral `moby_898` remix for playful sea stories

The bundled text files live in `src/smallwords/data/`. `moby_898`,
`basic_850`, and `special_english_1475` are direct source-backed lists.
`caveman_898`, `cowboy_898`, and `pirate_898` are derived size-neutral remixes
built on top of `moby_898`.

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

This paired example shows how the same meaning changes across natural, simple,
pirate, and cowboy wording. Each line below is an unedited local model output
from October 15, 2026. The runs used
`ibm-granite/granite-4.2-8b-GGUF` through `llama-server` from
`llama.cpp`.

The original run was unconstrained. The other three used generated GBNF from a
task-focused subset of the named preset. Each constrained result also passes
the same output-shape check against its full v0.2.0 preset.

The shared request was: *Greet a friend and say where you are.*

| Mode | Model output | v0.2.0 validation |
| --- | --- | --- |
| Original | “Hi, I'm home.” | Unconstrained |
| Simple (`moby_898`) | “Good day friend I am at home” | Passes |
| Pirate (`pirate_898`) | “Ahoy matey I am on the ship near the island.” | Passes |
| Cowboy (`cowboy_898`) | “Howdy friend I am at the ranch near the prairie” | Passes |

The focused subsets keep the generated grammar compact for a specific task;
they do not introduce words outside the underlying presets. The resulting lines
therefore demonstrate constrained generation rather than prompt-only style
guidance followed by validation.

## Examples

Start with the offline quick start above. For live-model examples, see the repository's
[`examples/README.md`](https://github.com/cmccomb/smallwords/blob/main/examples/README.md)
for the runnable examples. The bridge contrast, pirate greeting, and technical
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
