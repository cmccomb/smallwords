# Examples

Most of these examples stay runtime-agnostic on purpose and use the package's
built-in, source-backed wordlists. Each resource-building script prints a
prompt, its generated output resources, and a sample response that is validated
against the chosen word list.

Run them from the project root with the local virtualenv:

```bash
.venv/bin/python examples/customer_support_chat.py
.venv/bin/python examples/neighbor_intro_chat.py
.venv/bin/python examples/bridge_explain.py
.venv/bin/python examples/readme_bridge_contrast.py
```

Included scenarios:

- `customer_support_chat.py`: a short support-style reply built with `reasoning_250`
- `neighbor_intro_chat.py`: a friendly small-talk response built with `common_250`
- `bridge_explain.py`: a plain bridge explanation built with `common_250`
- `readme_bridge_contrast.py`: compares a real local Qwen bridge answer with the README's compliant `common_250` reference answer
