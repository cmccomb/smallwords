# smallwords

[![CI](https://github.com/cmccomb/smallwords/actions/workflows/ci.yml/badge.svg)](https://github.com/cmccomb/smallwords/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/smallwords)](https://pypi.org/project/smallwords/)
[![Python versions](https://img.shields.io/pypi/pyversions/smallwords)](https://pypi.org/project/smallwords/)
[![License](https://img.shields.io/github/license/cmccomb/smallwords)](https://github.com/cmccomb/smallwords/blob/main/LICENSE)

`smallwords` is a tiny Python package for controlled-vocabulary prompting plus
portable output resources. It helps you generate GBNF and JSON Schema artifacts
for small-word English responses, then validate text after generation if you
want an extra offline check.

The package ships with bundled source-backed wordlists, including short
frequency-based lists plus fuller `basic_850` and `special_english` presets.
By default, the built-ins also allow slight family variants such as `go`,
`goes`, and `going`.

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
from smallwords import allow_input_words, is_compliant, make_resources, out_of_vocab, prompt_explain_simply

spec = allow_input_words("common_250", "How does a bridge work?")
prompt = prompt_explain_simply("How does a bridge work?", wordlist=spec)
resources = make_resources(spec, max_words_per_line=9, max_lines=3)

gbnf = resources.gbnf
schema = resources.json_schema(key="answer")

text = "A bridge goes over water."
ok = is_compliant(text, spec)
missing = out_of_vocab("A bridge goes over water.", spec)
```

The prompt helpers include the full allowed vocabulary block, including
expanded forms such as `go`, `goes`, and `going`, so the model sees the soft
instruction as well as the hard grammar or schema.

If you want the model to be able to repeat topic or question terms such as
`bridge`, `neighbor`, or `order`, use `allow_input_words(...)` once and pass
that derived spec into the prompt, resources, and validation helpers together.

## Built-In Wordlists

- `common_50`: 50 high-frequency words from Moby `freq.txt`, filtered to Special English
- `common_100`: 100 high-frequency words from Moby `freq.txt`, filtered to Special English
- `common_250`: 250 high-frequency words from Moby `freq.txt`, filtered to Special English
- `basic_850`: Charles Ogden's Basic English 850
- `special_english`: Voice of America Special English
- `reasoning_250`: `common_250` plus a small planning supplement for visible plan blocks
- `caveman_250`: a surface-only `common_250` remix with caveman extras and fewer helper words
- `pirate_250`: a playful `common_250` remix with pirate extras

The bundled text files live in `src/smallwords/data/`. The `common_*` lists are
derived from Project Gutenberg's Moby Words II frequency list and filtered
through Special English. `basic_850` and `special_english` are bundled from the
MIT-licensed J. Burkardt dataset mirror.

The themed remixes live in `src/smallwords/caveman.py` and
`src/smallwords/pirate.py`. If you want to build your own, use
`remix_wordlist(...)` with a base list plus curated additions and removals.

## Contrastive Example

This is the clearest way to see what `smallwords` is trying to do. Both blocks
below are genuine local Qwen outputs from April 4, 2026. The first uses a plain
prompt. The second uses the same base prompt plus an explicit `basic_850`
vocabulary list, the topic word `bridge`, and the generated GBNF.

A plain prompt stays fairly natural:

> A bridge provides a structure that spans a gap, such as a river or valley,
> to allow safe passage over it.

A constrained `basic_850 + topic words` run is simpler, though still stiffer:

> A bridge is a structure that goes across a river or road to connection.

These runs use `llama.cpp` and
[`Qwen/Qwen3-4B-Instruct-2507`](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507)
via
[`bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF`](https://huggingface.co/bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF).

Reproduce that comparison from a clone of the repository with:

```bash
python examples/readme_bridge_contrast.py
```

## Examples

See the repository's
[`examples/README.md`](https://github.com/cmccomb/smallwords/blob/main/examples/README.md)
for the runnable examples. The bridge, neighbor, and customer-support scripts
all print prompts, resources, and compliant sample outputs built from the
bundled wordlists, with optional task-word expansion where it helps.

## Development

```bash
python -m pip install -e ".[dev]"
ruff check .
ruff format .
pytest
python scripts/check_documentation.py
python -m build
python -m twine check --strict dist/*
```

CI runs tests, the documentation policy check, and a package build on GitHub
Actions.

For release steps and Trusted Publishing setup, see
[`RELEASING.md`](https://github.com/cmccomb/smallwords/blob/main/RELEASING.md).
