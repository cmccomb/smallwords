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

Pirate Welcome
~~~~~~~~~~~~~~

This example addresses a different problem: themed language usually depends on
small lexical choices rather than a large prompt scaffold. The pirate remix
keeps the base vocabulary compact, adds task words back in, and then constrains
generation through the same resource bundle.

.. code-block:: python

   from smallwords import allow_input_words, make_resources, prompt_answer_simply

   question = "Give a short pirate-style greeting for a new friend."
   spec = allow_input_words("pirate_898", question)
   prompt = prompt_answer_simply(question, wordlist=spec)
   resources = make_resources(spec, max_words_per_line=12, max_lines=1)

Constrained result:

   Ahoy,

The pirate example is intentionally playful, which makes it a useful check on
whether a themed remix remains usable rather than merely novel.

Technical Rewrite
~~~~~~~~~~~~~~~~~

Rewriting technical text introduces another bottleneck. The system must retain
the source meaning while moving into a simpler vocabulary. A broad prompt can
request that shift, but it does not define which words remain available. This
example uses ``special_english_1475`` plus the source passage terms so the
rewrite stays interpretable and inspectable.

.. code-block:: python

   from smallwords import allow_input_words, make_resources, prompt_rewrite_simply

   text = (
       "The navigation stack estimates the robot position by combining wheel "
       "encoder readings, inertial measurements, and camera landmarks several "
       "times each second."
   )
   spec = allow_input_words("special_english_1475", text)
   prompt = prompt_rewrite_simply(text, wordlist=spec)
   resources = make_resources(spec, max_words_per_line=16, max_lines=1)

Constrained result:

   The navigation stack finds where the robot is by using wheel encoder readings,

The live scripts in ``examples/`` print the full prompt, grammar, schema, and
validation details. That fuller output matters because it lets a reader inspect
not only the answer, but also the exact constraint setup that produced it.
