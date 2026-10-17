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
prompt text, GBNF, JSON Schema, and full output validation that stay aligned.

Install
-------

.. code-block:: bash

   pip install smallwords

Quick API
---------

Most integrations follow the same chain: choose a vocabulary, optionally add
task words, build the matching prompt and portable resources, then validate the
result.

For a first run without a model server, use
``python examples/offline_quickstart.py`` from a repository checkout.
Pass only essential terms to ``allow_input_words``: supplying an entire source
passage allows all its uncommon words in the generated response.

.. autofunction:: smallwords.allow_input_words

.. autofunction:: smallwords.get_wordlist

.. autofunction:: smallwords.list_wordlists

.. autoclass:: smallwords.OutputShape
   :members:

.. autoclass:: smallwords.OutputResources
   :members:

.. autoclass:: smallwords.OutputValidation

.. autofunction:: smallwords.validate_output

.. autofunction:: smallwords.prompts.build_prompt

.. autofunction:: smallwords.is_compliant

.. autofunction:: smallwords.is_in_vocabulary

.. autofunction:: smallwords.out_of_vocab

``OutputResources.validate`` and ``validate_output`` check the full vocabulary
and output shape. ``is_compliant`` and ``out_of_vocab`` check alphabetic word
membership only; they ignore numbers, punctuation, capitalization, and line
limits.

``allow_input_words`` extracts runs of Unicode letters and combining marks
between delimiters. An unspaced Japanese run is treated as one literal; the
helper does not perform language-specific word segmentation or inflection.
Unicode spellings are exact after lowercasing, so precomposed and decomposed
accents remain distinct. A valid full-contract response has no out-of-vocabulary
issue; diagnostics for invalid output are best-effort token reports.

Built-ins
---------

The installed catalog currently includes:

- ``moby_898``
- ``basic_850``
- ``special_english_1475``
- ``caveman_898``
- ``cowboy_898``
- ``pirate_898``

Use :func:`smallwords.list_wordlists` to inspect the installed catalog. Use
:func:`smallwords.get_wordlist` when a workflow needs the underlying
specification object directly.

``caveman_898`` now contains 355 hand-curated, one-syllable words with chiefly
Germanic roots. It retains eight plain exceptions for usefulness: ``fur``,
``leach``, ``oil``, ``rock``, ``tent``, ``wall``, ``war``, and ``plant``. Its
name refers to its ``moby_898`` starting point. The complete removed-word list
is in ``docs/caveman_removed_words.txt``.

The ``cowboy_898`` and ``pirate_898`` presets each replace 40 abstract base
words with themed terms and everyday pronouns. ``build_prompt`` includes their
voice guidance; GBNF and JSON Schema enforce vocabulary and output shape only.
These are playful styles rather than historical dialect models. See the
`National Park Service cowboy history <https://www.nps.gov/tapr/learn/historyculture/cowboys.htm>`_
and `Royal Museums Greenwich pirate word guide <https://www.rmg.co.uk/press-release/international-talk-pirate-weekend>`_
for source context.

Run ``python examples/themed_presets.py`` for offline samples of both presets.

Examples With Results
---------------------

The comparison below was produced locally on October 15, 2026 with
``llama-server`` and ``ibm-granite/granite-4.2-8b-GGUF``.

Missile Guidance Contrast
~~~~~~~~~~~~~~~~~~~~~~~~~

This comparison starts with the opening sentence and a compressed later line
from the missile-guidance monologue. Six constrained rewrites express the same
idea as a current place, a target place, and the span between them.

.. code-block:: python

   from smallwords import OutputResources, OutputShape, allow_input_words
   from smallwords.prompts import build_prompt

   source = (
       "The missile knows where it is at all times. "
       "By subtracting where it is from where it isn't, or where it isn't from "
       "where it is, it obtains a difference, or deviation."
   )
   spec = allow_input_words("moby_898", "missile")
   shape = OutputShape(min_words_per_line=6, max_words_per_line=11, max_lines=3)
   prompt = build_prompt("explain", source, wordlist=spec)
   resources = OutputResources.from_wordlist(spec, shape=shape)

Original source::

   The missile knows where it is at all times. By subtracting where it is from where it isn't, or where it isn't from where it is, it obtains a difference, or deviation.

Simple, constrained with ``moby_898`` plus ``missile``::

   The missile knows where it is at all times.
   It knows where it should be next.
   The difference tells it how far to move.

Caveman, constrained with ``caveman_898``::

   Rock know where it be now.
   Rock know where it should be.
   Rock know how far it must go.

Basic English, constrained with ``basic_850``::

   The thing has knowledge of where the thing is now.
   The thing is to be at the other place.
   The distance from here to there is how far to move.

Special English, constrained with ``special_english_1475``::

   The missile knows where it is at all times.
   It should be at the second place.
   The distance tells how far to move from here to there.

Pirate, constrained with ``pirate_898``::

   The ship knows where it is now.
   The crew knows where the ship should be.
   The difference tells the crew which way to sail.

Cowboy, constrained with ``cowboy_898``::

   The cowboy knows where the cattle are now.
   The ranch is where the cattle should be.
   The difference tells the cowboy which way to ride.

The live run uses a compact task-focused subset for each grammar. It then checks
the result against both that subset and the complete preset. Only the simple
case adds a topic word, ``missile``. See
``examples/readme_missile_contrast.py`` for all six prompts, grammars, schemas,
model calls, and validation reports.

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
       style_hint="Use a friendly pirate greeting.",
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
