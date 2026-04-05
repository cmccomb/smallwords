"""Sphinx configuration for the compact project docs site."""

from __future__ import annotations

import sys
from pathlib import Path

# Add the source tree so autodoc can import the local package during docs builds.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from smallwords import __version__  # noqa: E402

project = "smallwords"
author = "Christopher McComb"
copyright = "2026, Christopher McComb"
version = __version__
release = __version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
autodoc_member_order = "bysource"
autodoc_typehints = "description"
napoleon_google_docstring = True
napoleon_numpy_docstring = False

html_theme = "pydata_sphinx_theme"
html_title = "smallwords"
html_theme_options = {
    "github_url": "https://github.com/cmccomb/smallwords",
    "show_toc_level": 2,
}
