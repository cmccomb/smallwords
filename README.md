# smallwords

[![CI](https://github.com/cmccomb/smallwords/actions/workflows/ci.yml/badge.svg)](https://github.com/cmccomb/smallwords/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcmccomb%2Fsmallwords%2Fmain%2F.github%2Fbadges%2Fcoverage.json)](https://github.com/cmccomb/smallwords/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/smallwords)](https://pypi.org/project/smallwords/)
[![Python versions](https://img.shields.io/pypi/pyversions/smallwords)](https://pypi.org/project/smallwords/)
[![License](https://img.shields.io/github/license/cmccomb/smallwords)](https://github.com/cmccomb/smallwords/blob/main/LICENSE)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-4c1)](https://cmccomb.github.io/smallwords/)

`smallwords` is a tiny Python package for controlled-vocabulary prompting plus
portable output resources. It helps you generate GBNF and JSON Schema artifacts
for small-word English responses, then validate text after generation if you
want an extra offline check.

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

For local development:

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from smallwords import (
    allow_input_words,
    is_compliant,
    make_gbnf,
    make_json_schema,
    prompt_explain_simply,
)

plain_prompt = "Explain what a bridge does in one short sentence."

spec = allow_input_words("basic_850", "How does a bridge work?")
smallwords_prompt = prompt_explain_simply("How does a bridge work?", wordlist=spec)
gbnf = make_gbnf(spec, max_words_per_line=24, max_lines=1)
schema = make_json_schema(
    spec,
    key="answer",
    title="bridge_explanation",
    max_words_per_line=24,
    max_lines=1,
)

text = "A bridge is a structure that helps people and things move across a river or a deep place."
ok = is_compliant(text, spec)
```

The contrast is the point. `plain_prompt` is the soft instruction you would use
for an unconstrained run. `smallwords_prompt + gbnf` is the tighter version:
the model sees the same task, an explicit allowed vocabulary block, and a hard
output constraint that another runtime can reuse.

The prompt helpers include the full allowed vocabulary block, including
expanded forms such as `go`, `goes`, and `going`, so the model sees the soft
instruction as well as the hard grammar or schema.

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
`moby_898`. Output formatting modes such as visible planning blocks are
configured through `thinking_mode`; they are not separate wordlists.

The themed remixes live in `src/smallwords/themes/caveman.py` and
`src/smallwords/themes/pirate.py`. If you want to build your own, use
`remix_wordlist(...)` with a base list plus curated additions and removals.

For source-tree navigation, `src/smallwords/` is now organized into a few
clear groups: core runtime-agnostic modules at the package root, bundled data
files in `data/`, themed remixes in `themes/`, and optional runtime helpers in
`integrations/`.

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

Reproduce that comparison from a clone of the repository with:

```bash
llama-server -hf bartowski/Qwen_Qwen3-8B-GGUF:q4_k_m --host 127.0.0.1 --port 8080 --reasoning-budget 0 --log-disable
python examples/readme_bridge_contrast.py
```

## Examples

See the repository's
[`examples/README.md`](https://github.com/cmccomb/smallwords/blob/main/examples/README.md)
for the runnable examples. The current example set is live-model based:
eclectic themed welcomes, a technical rewrite, and the README bridge contrast
all call a live `llama-server` model with a prompt plus generated grammar.
Start a server once, then run whichever example you want. If your server is not
on `http://127.0.0.1:8080`, set `SMALLWORDS_LLAMA_BASE_URL`.

## Development

```bash
python -m pip install -e ".[dev]"
ruff check .
ruff format .
pytest
pytest --cov=smallwords --cov-report=term-missing
python scripts/check_documentation.py
python -m sphinx -W --keep-going -b html docs docs/_build/html
python -m build
python -m twine check --strict dist/*
```

CI runs linting, tests, the documentation policy check, a `>=90%` coverage
gate, a Sphinx docs build, and a package build on GitHub Actions.

For release steps and Trusted Publishing setup, see
[`RELEASING.md`](https://github.com/cmccomb/smallwords/blob/main/RELEASING.md).
