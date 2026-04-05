smallwords
==========

Large language models can follow “write simply” instructions, but that soft
guidance is often insufficient when a workflow also needs reproducible wording,
portable output constraints, or offline validation. Prompt-only approaches are
easy to start and hard to trust. They leave the active vocabulary implicit,
make failures difficult to diagnose, and force each integration to recreate the
same constraint logic in a different format.

``smallwords`` addresses that gap by keeping one controlled vocabulary at the
center of the workflow. From that single specification, the package can build
prompt text, GBNF, JSON Schema, and validation checks that stay aligned. This
page therefore does two things. First, it identifies the small public API that
most callers actually need. Second, it shows a few live-model examples with
real outputs so the package can be evaluated in operational terms rather than
through abstract claims.

Install
-------

.. code-block:: bash

   pip install smallwords

Quick API
---------

Most integrations follow the same chain: choose a vocabulary, optionally add
task words, build the matching resources, then validate the result. The
functions below are the core entry points for that flow.

.. autofunction:: smallwords.allow_input_words

.. autofunction:: smallwords.make_resources

.. autofunction:: smallwords.make_gbnf

.. autofunction:: smallwords.make_json_schema

.. autofunction:: smallwords.prompt_explain_simply

.. autofunction:: smallwords.prompt_rewrite_simply

.. autofunction:: smallwords.prompt_answer_simply

.. autofunction:: smallwords.is_compliant

.. autofunction:: smallwords.out_of_vocab

.. autoclass:: smallwords.OutputResources
   :members:

Built-ins
---------

The package root also exports a small set of ready-made bundles. These presets
cover the main trade-off space from more permissive general English to themed
remixes:

- ``MOBY_898``
- ``BASIC_850``
- ``SPECIAL_ENGLISH_1475``
- ``CAVEMAN_898``
- ``PIRATE_898``

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
the prompt, and applies the matching grammar. That shift makes the output more
auditable and more portable across integrations.

.. code-block:: python

   from smallwords import allow_input_words, make_resources, prompt_explain_simply

   spec = allow_input_words("basic_850", "How does a bridge work?")
   prompt = prompt_explain_simply("How does a bridge work?", wordlist=spec)
   resources = make_resources(spec, max_words_per_line=24, max_lines=1)

Plain prompt result:

   A bridge connects two points, usually across a body of water or a gap, allowing people and vehicles to cross safely.

Constrained result:

   A bridge is a structure that helps people and things move across a river or a deep place.

See ``examples/readme_bridge_contrast.py`` for the full prompt-plus-grammar run.

Pirate Greeting
~~~~~~~~~~~~~~~

This example addresses a different problem: themed language depends on small
lexical choices, but a large themed vocabulary can still give the model too
many awkward legal paths. The response here is narrower. It starts from the
built-in ``pirate_898`` list, selects a tiny greeting-focused surface
vocabulary, and then applies a matching grammar. That change keeps the example
playful while making the live behavior cleaner and faster.

.. code-block:: python

   from smallwords import WordlistSpec, get_wordlist, make_resources

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
   resources = make_resources(spec, min_words_per_line=6, max_words_per_line=6, max_lines=1)

Constrained result:

   Ahoy matey good to meet you.

The pirate example is intentionally playful, which makes it a useful check on
whether a themed remix remains usable rather than merely novel.

Technical Rewrite
~~~~~~~~~~~~~~~~~

Rewriting technical text introduces another bottleneck. The system must retain
the source meaning while moving into a simpler vocabulary. A broad prompt can
request that shift, but it does not define which words remain available. A very
large allowed-word block can also leave too much room for weak paraphrases. The
example below responds by selecting a compact rewrite vocabulary from
``basic_850`` that excludes the source terminology altogether. That makes the
rewrite narrower, but also much easier to inspect.

.. code-block:: python

   from smallwords import WordlistSpec, get_wordlist, make_resources

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
   resources = make_resources(spec, min_words_per_line=10, max_words_per_line=10, max_lines=1)

Constrained result:

   When engine heat is very high this system cuts power.

The live scripts in ``examples/`` print the full prompt, grammar, schema, and
validation details. That fuller output matters because it lets a reader inspect
not only the answer, but also the exact constraint setup that produced it.
