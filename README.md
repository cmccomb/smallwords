# smallwords

`smallwords` is a tiny Python package for controlled-vocabulary prompting plus
portable output resources. It helps you generate GBNF and JSON Schema artifacts
for small-word English responses, then validate text after generation if you
want an extra offline check.

The package ships with bundled source-backed wordlists, including short
frequency-based lists plus fuller `basic_850` and `special_english` presets.

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
from smallwords import COMMON_250, is_compliant, make_resources, out_of_vocab, prompt_explain_simply

prompt = prompt_explain_simply("How does a bridge work?", wordlist="common_250")
resources = make_resources("common_250", max_words_per_line=9, max_lines=3)

gbnf = resources.gbnf
schema = resources.json_schema(key="answer")

text = "A way can go over water."
ok = is_compliant(text, "common_250")
missing = out_of_vocab("A bridge can go over water.", "common_250")
```

## Built-In Wordlists

- `common_50`: 50 high-frequency words from Moby `freq.txt`, filtered to Special English
- `common_100`: 100 high-frequency words from Moby `freq.txt`, filtered to Special English
- `common_250`: 250 high-frequency words from Moby `freq.txt`, filtered to Special English
- `basic_850`: Charles Ogden's Basic English 850
- `special_english`: Voice of America Special English
- `reasoning_250`: `common_250` plus a small planning supplement for visible plan blocks

The bundled text files live in `src/smallwords/data/`. The `common_*` lists are
derived from Project Gutenberg's Moby Words II frequency list and filtered
through Special English. `basic_850` and `special_english` are bundled from the
MIT-licensed J. Burkardt dataset mirror.

## Contrastive Example

This is the clearest way to see what `smallwords` is trying to do.

A real local Qwen response to a normal prompt is still fairly technical:

> A bridge is a structure built to span a physical obstacle like a river or
> valley, providing a path for people, vehicles, or trains to cross. It works
> by transferring the weight of the load and its own structure through beams,
> arches, or suspension cables to the supports on either side. This distribution
> of forces ensures stability and safety, allowing the bridge to carry weight
> without collapsing.

A `smallwords`-style `common_250` target for the same idea is much plainer:

> A way can go over water.
> Each part hold people up.
> The force move down through each side.

The first block is a genuine local Qwen output from April 4, 2026 using
`llama.cpp` and
[`Qwen/Qwen3-4B-Instruct-2507`](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507)
via
[`bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF`](https://huggingface.co/bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF).
The second block is the compliant `common_250` reference answer used by the
package examples.

Reproduce that comparison locally with:

```bash
.venv/bin/python examples/readme_bridge_contrast.py
```

## Examples

See [`examples/README.md`](examples/README.md) for the runnable examples. The
bridge, neighbor, and customer-support scripts all print prompts, resources,
and compliant sample outputs built from the bundled wordlists.

## Development

```bash
pytest
python scripts/check_documentation.py
python -m build
```

CI runs tests, the documentation policy check, and a package build on GitHub
Actions.
