# smallwords

Starter package for constrained simple-language generation with llama.cpp / llama-cpp-python.

This starter intentionally ships with small built-in demo wordlists so you can wire up the API,
grammar generation, and prompt templates quickly. Once you pick your canonical sources, replace or
extend the lists in `src/smallwords/wordlists.py`.

## Quick start

```python
from smallwords import COMMON_50, COMMON_50_THINKING, prompt_explain_simply

prompt = prompt_explain_simply("How does a bridge work?", wordlist="common_50")
grammar = COMMON_50.to_llama_grammar()  # requires llama-cpp-python
```

## Design notes

- `PrebuiltGrammar` lazily compiles a `llama_cpp.LlamaGrammar` only when needed.
- Prompt helpers are separate from grammar helpers.
- Validation helpers let you check text outside constrained decoding.
