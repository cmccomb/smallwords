# smallwords

`smallwords` is a tiny Python package for controlled-vocabulary prompting plus
portable output resources. It helps you generate GBNF and JSON Schema artifacts
for small-word English responses, then validate text after generation if you
want an extra offline check.

The package ships with bundled source-backed wordlists so you can wire up the
API quickly without leaning on placeholder demo vocabularies.

## What It Includes

- Prompt helpers for explaining, summarizing, rewriting, and answering in plain English
- Reusable `OutputResources` bundles for bundled source-backed wordlists
- Portable GBNF resources you can hand to any compatible runtime
- Strict single-key JSON Schema helpers for structured-output APIs
- Validation helpers to find out-of-vocabulary words in model output
- A backend-agnostic public API with no required model runtime dependency

## Installation

Install the package itself:

```bash
pip install smallwords
```

Install local development tools:

```bash
pip install -e ".[dev]"
```

## Quick Start

Use prompt helpers when you want a plain instruction template:

```python
from smallwords import prompt_explain_simply

prompt = prompt_explain_simply(
    "How does a bridge work?",
    wordlist="common_50",
)
```

Use a prebuilt resource bundle when you want constrained decoding:

```python
from smallwords import COMMON_50, prompt_explain_simply

resources = COMMON_50
prompt = prompt_explain_simply("How does a bridge work?", wordlist="common_50")
gbnf = resources.gbnf
```

Use JSON Schema when your client expects structured outputs:

```python
from smallwords import COMMON_50

schema = COMMON_50.json_schema(key="answer")
```

Validate text after generation if you are not decoding with a grammar:

```python
from smallwords import is_compliant, out_of_vocab

text = "The man can make a bridge."
ok = is_compliant("The man can make it.", "common_50")
missing = out_of_vocab(text, "common_50")
```

## Built-In Wordlists

- `common_50`: 50 high-frequency words from Moby `freq.txt`, filtered to Special English
- `common_100`: 100 high-frequency words from Moby `freq.txt`, filtered to Special English
- `common_250`: 250 high-frequency words from Moby `freq.txt`, filtered to Special English
- `basic_850`: Charles Ogden's Basic English 850
- `special_english`: Voice of America Special English
- `reasoning_250`: `common_250` plus a small planning supplement for visible plan blocks

## Wordlist Sources

The built-in vocabularies are bundled as normalized text resources under
`src/smallwords/data/`:

- `common_*`: derived from Project Gutenberg's Moby Words II frequency list and
  filtered through the Special English vocabulary so the short tiers stay
  simple while still following a real frequency ranking.
- `basic_850`: bundled from the MIT-licensed J. Burkardt dataset mirror of
  Basic English 850.
- `special_english`: bundled from the MIT-licensed J. Burkardt dataset mirror
  of Voice of America Special English.

## Core Concepts

`OutputResources` wraps a `WordlistSpec` plus output options such as
`thinking_mode`, `max_words_per_line`, and `max_lines`. Its `.gbnf` property
builds the GBNF resource lazily, and `.json_schema()` emits a strict single-key
JSON Schema whose value is constrained by a generated regex.

Prompt helpers and grammar helpers are separate on purpose. You can use prompt
templates alone, resource-constrained decoding alone, or both together.

Validation helpers are meant for offline checks and tests. They normalize text
into lowercase word tokens and report tokens that are not present in the chosen
word list.

## Applied Examples

See [`examples/README.md`](examples/README.md) for four runnable scenarios:

- `examples/customer_support_chat.py`: a support-style reply built with `reasoning_250`
- `examples/neighbor_intro_chat.py`: a friendly small-talk reply built with `common_250`
- `examples/bridge_explain.py`: a bridge explanation built with `common_250`
- `examples/readme_bridge_contrast.py`: reruns the real local Qwen bridge comparison used below

Run any example from the project root:

```bash
.venv/bin/python examples/bridge_explain.py
```

## Contrastive Example

The bridge example is a good way to see the tone shift this package is aiming
for. The two responses below were generated locally on April 4, 2026 with
`llama.cpp` and the `Q4_K_M` GGUF quantization of
[`Qwen/Qwen3-4B-Instruct-2507`](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507)
from
[`bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF`](https://huggingface.co/bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF).

Reproduce this exact comparison locally with:

```bash
.venv/bin/python examples/readme_bridge_contrast.py
```

Standard bridge prompt:

> A bridge is a structure built to span a physical obstacle like a river or
> valley, providing a path for people, vehicles, or trains to cross. It works
> by transferring the weight of the load and its own structure through beams,
> arches, or suspension cables to the supports on either side. This distribution
> of forces ensures stability and safety, allowing the bridge to carry weight
> without collapsing.

Simple bridge prompt:

> A bridge is a structure built over a river, road, or gap so cars, bikes, or
> people can go from one side to the other. It's like a big, strong path that
> spans the gap without falling through. The bridge holds up with strong
> supports, like legs, so it doesn't collapse.

The second answer is still a real model output, but it is noticeably plainer.
`smallwords` is meant to make that simpler mode reproducible and enforceable
with reusable prompts, GBNF, and JSON Schema resources.

## Example Workflow

```python
from smallwords import COMMON_250, is_compliant, make_resources, prompt_answer_simply

question = "Why do plants need light?"
prompt = prompt_answer_simply(question, wordlist="common_250")
resources = make_resources("common_250", max_words_per_line=12, max_lines=4)

# send `prompt`, `resources.gbnf`, or `resources.json_schema(...)` to your model runtime here
text = "Plants need light to make food."

assert is_compliant(text, "common_250")
```

## Development

Run the local test suite:

```bash
pytest
```

Run the documentation policy check:

```bash
python scripts/check_documentation.py
```

Build a source distribution and wheel:

```bash
python -m build
```

## CI

The repository includes a GitHub Actions workflow at
`.github/workflows/ci.yml`. It runs the test suite across supported Python
versions and performs a package build check so releases do not drift away from
what developers run locally.
