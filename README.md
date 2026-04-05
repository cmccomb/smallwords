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
lists such as `moby_898`, `basic_850`, and `special_english_1475`, plus a
couple of intentionally themed remixes. By default, the built-ins also allow
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
from smallwords import OutputResources, OutputShape, allow_input_words, is_compliant
from smallwords.prompts import build_prompt

shape = OutputShape(max_words_per_line=24, max_lines=1)
spec = allow_input_words("basic_850", "How does a bridge work?")
resources = OutputResources.from_wordlist(spec, shape=shape)
prompt = build_prompt("explain", "How does a bridge work?", wordlist=spec)
schema = resources.json_schema(key="answer", title="bridge_explanation")

text = "A bridge is a structure that helps people and things move across a river or a deep place."
ok = is_compliant(text, spec)
```

The contrast is the point. `build_prompt(...)` is the soft instruction layer.
`OutputResources` gives you the matching hard constraints in both GBNF and JSON
Schema form. `is_compliant(...)` is the lightweight offline check.

If you want the model to be able to repeat topic or question terms such as
`bridge`, `neighbor`, or `order`, use `allow_input_words(...)` once and pass
that derived spec into the prompt, resources, and validation helpers together.

## Built-In Wordlists

- `moby_898`: the full normalized alpha-only Moby Words II frequency list
- `basic_850`: Charles Ogden's Basic English 850
- `special_english_1475`: Voice of America Special English
- `caveman_898`: a size-neutral surface-only `moby_898` remix with caveman adjustments
- `pirate_898`: a size-neutral `moby_898` remix with pirate adjustments

The bundled text files live in `src/smallwords/data/`. `moby_898`,
`basic_850`, and `special_english_1475` are direct source-backed lists.
`caveman_898` and `pirate_898` are derived size-neutral remixes built on top of
`moby_898`.

The themed remixes live in `src/smallwords/themes/caveman.py` and
`src/smallwords/themes/pirate.py`. If you want to build your own, use
`remix_wordlist(...)` with a base list plus curated additions and removals.

## Contrastive Example

This is the clearest way to see what `smallwords` is trying to do. Both blocks
below are genuine local Qwen outputs from April 5, 2026. The first uses a plain
prompt. The second uses the same base prompt plus an explicit `basic_850`
vocabulary list, the topic word `bridge`, and the generated GBNF.

A plain prompt stays fairly natural:

> A bridge connects two points, usually across a body of water or a gap,
> allowing people and vehicles to cross safely.

A constrained `basic_850 + topic words` run stays simpler while still sounding
reasonably natural:

> A bridge is a structure that helps people and things move across a river or a
> deep place.

These runs use `llama-server` from `llama.cpp` and
[`Qwen/Qwen3-8B-GGUF`](https://huggingface.co/Qwen/Qwen3-8B-GGUF)
via
[`bartowski/Qwen_Qwen3-8B-GGUF`](https://huggingface.co/bartowski/Qwen_Qwen3-8B-GGUF).

Reproduce that comparison from a clone of the repository with an activated
virtualenv:

```bash
llama-server -hf bartowski/Qwen_Qwen3-8B-GGUF:q4_k_m --host 127.0.0.1 --port 8080 --reasoning-budget 0 --log-disable
python examples/readme_bridge_contrast.py
```

## Examples

See the repository's
[`examples/README.md`](https://github.com/cmccomb/smallwords/blob/main/examples/README.md)
for the runnable examples. The current example set is live-model based:
the README bridge contrast, a focused pirate greeting, and a focused technical
rewrite all call a live `llama-server` model with a prompt plus generated
grammar.

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
