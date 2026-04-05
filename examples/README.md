# Examples

This directory keeps three live llama.cpp examples:

- `readme_bridge_contrast.py`: the bridge comparison used in the root README
- `pirate_greeting.py`: a focused pirate greeting built from `pirate_898`
- `rewrite_technical_passage.py`: a focused technical rewrite built from `basic_850`

Create and activate a virtualenv first:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Then start a server, for example:

```bash
llama-server -hf bartowski/Qwen_Qwen3-8B-GGUF:q4_k_m --host 127.0.0.1 --port 8080 --reasoning-budget 0 --log-disable
```

Run the examples from the project root:

```bash
python examples/pirate_greeting.py
python examples/rewrite_technical_passage.py
python examples/readme_bridge_contrast.py
```

If your server uses a different address, set `SMALLWORDS_LLAMA_BASE_URL`.

Each script prints the prompt, output shape, matching grammar and schema
resources, the generated response, and whether the response stayed inside the
chosen vocabulary.
