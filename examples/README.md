# Examples

This directory now keeps just three examples:

- `readme_bridge_contrast.py`: the live bridge comparison used in the root README
- `eclectic_welcomes.py`: a live caveman-versus-pirate welcome comparison built from `caveman_898` and `pirate_898`
- `rewrite_technical_passage.py`: a live technical-to-simple rewrite built from `special_english_1475` plus the source passage words

Run them from the project root with the local virtualenv:

```bash
.venv/bin/python examples/eclectic_welcomes.py
.venv/bin/python examples/rewrite_technical_passage.py
.venv/bin/python examples/readme_bridge_contrast.py
```

All three examples use a live `llama.cpp` model through `llama-server`. Start a
server first, for example:

```bash
llama-server -hf bartowski/Qwen_Qwen3-8B-GGUF:q4_k_m --host 127.0.0.1 --port 8080 --reasoning-budget 0 --log-disable
```

If your server uses a different address, set `SMALLWORDS_LLAMA_BASE_URL`.

Each script prints the prompt, matching grammar and schema resources, the
generated response, and whether the response stayed inside the chosen
vocabulary. The bridge contrast example is the heaviest because it also runs an
unconstrained comparison prompt for the README.
