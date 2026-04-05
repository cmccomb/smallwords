smallwords
==========

Large language models can follow "write simply" instructions, but that soft
guidance is often insufficient when a workflow also needs reproducible wording,
portable output constraints, or offline validation. Prompt-only approaches are
easy to start and hard to trust. They leave the active vocabulary implicit,
make failures difficult to diagnose, and force each integration to recreate the
same constraint logic in a different format.

``smallwords`` addresses that gap by keeping one controlled vocabulary at the
center of the workflow. From that single specification, the package can build
prompt text, GBNF, JSON Schema, and validation checks that stay aligned.

Install
-------

.. code-block:: bash

   pip install smallwords

Quick API
---------

Most integrations follow the same chain: choose a vocabulary, optionally add
task words, build the matching prompt and portable resources, then validate the
result.

.. autofunction:: smallwords.allow_input_words

.. autofunction:: smallwords.get_wordlist

.. autofunction:: smallwords.list_wordlists

.. autoclass:: smallwords.OutputShape
   :members:

.. autoclass:: smallwords.OutputResources
   :members:

.. autofunction:: smallwords.prompts.build_prompt

.. autofunction:: smallwords.is_compliant

.. autofunction:: smallwords.out_of_vocab

Built-ins
---------

The installed catalog currently includes:

- ``moby_898``
- ``basic_850``
- ``special_english_1475``
- ``caveman_898``
- ``pirate_898``

Use :func:`smallwords.list_wordlists` to inspect the installed catalog. Use
:func:`smallwords.get_wordlist` when a workflow needs the underlying
specification object directly.

Examples With Results
---------------------

The examples below were produced locally on April 5, 2026 with
``llama-server`` and ``bartowski/Qwen_Qwen3-8B-GGUF:q4_k_m``.

Bridge Contrast
~~~~~~~~~~~~~~~

This comparison isolates the package's core claim. A plain prompt can already
produce a reasonable answer. However, it does not expose an explicit response
contract. The constrained run uses the same task, adds the active vocabulary to
the prompt, and applies the matching grammar.

.. code-block:: python

   from smallwords import OutputResources, OutputShape, allow_input_words
   from smallwords.prompts import build_prompt

   spec = allow_input_words("basic_850", "How does a bridge work?")
   shape = OutputShape(max_words_per_line=24, max_lines=1)
   prompt = build_prompt("explain", "How does a bridge work?", wordlist=spec)
   resources = OutputResources.from_wordlist(spec, shape=shape)

Plain prompt result:

   A bridge connects two points, usually across a body of water or a gap, allowing people and vehicles to cross safely.

Constrained result:

   A bridge is a structure that helps people and things move across a river or a deep place.

See ``examples/readme_bridge_contrast.py`` for the full prompt-plus-grammar run.

Pirate Greeting
~~~~~~~~~~~~~~~

This example starts from the built-in ``pirate_898`` list, selects a tiny
greeting-focused vocabulary, and then applies a matching grammar.

.. code-block:: python

   from smallwords import OutputResources, OutputShape, WordlistSpec, get_wordlist
   from smallwords.prompts import build_prompt

   base = get_wordlist("pirate_898")
   spec = WordlistSpec(
       name="pirate_898_greeting_focus",
       words=("ahoy", "good", "matey", "meet", "to", "you"),
       source_name="Selected surface forms from pirate_898 for the pirate greeting example",
       source_urls=base.source_urls,
       license_name=base.license_name,
       allowed_punctuation=(".",),
       variant_mode="surface_only",
   )
   shape = OutputShape(min_words_per_line=6, max_words_per_line=6, max_lines=1)
   prompt = build_prompt(
       "answer",
       "A pirate meets a new friend on a ship. What short friendly greeting should the pirate say?",
       wordlist=spec,
   )
   resources = OutputResources.from_wordlist(spec, shape=shape)

Constrained result:

   Ahoy matey good to meet you.

Technical Rewrite
~~~~~~~~~~~~~~~~~

This example selects a compact rewrite vocabulary from ``basic_850`` that
excludes the source terminology altogether. The output shape then forces one
short ten-word sentence.

.. code-block:: python

   from smallwords import OutputResources, OutputShape, WordlistSpec, get_wordlist
   from smallwords.prompts import build_prompt

   base = get_wordlist("basic_850")
   text = (
       "The thermal controller derates propulsion output after the sensor array "
       "reports an overtemperature fault."
   )
   spec = WordlistSpec(
       name="basic_850_rewrite_focus",
       words=("be", "cut", "engine", "heat", "high", "if", "power", "system", "this", "very", "when"),
       source_name="Selected from basic_850 for the rewrite example",
       source_urls=base.source_urls,
       license_name=base.license_name,
       allowed_punctuation=(".",),
   )
   shape = OutputShape(min_words_per_line=10, max_words_per_line=10, max_lines=1)
   prompt = build_prompt("rewrite", text, wordlist=spec)
   resources = OutputResources.from_wordlist(spec, shape=shape)

Constrained result:

   When engine heat is very high this system cuts power.

The live scripts in ``examples/`` print the full prompt, grammar, schema, and
validation details. That fuller output matters because it lets a reader inspect
not only the answer, but also the exact constraint setup that produced it.
