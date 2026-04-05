"""Theme-specific wordlist remixes.

This subpackage groups the intentionally opinionated vocabulary remixes so they
are easy to find without mixing them into the core source-backed wordlist
catalog modules.
"""

# These re-exports keep the themed remix builders discoverable inside the package.
from .caveman import build_caveman_spec
from .pirate import build_pirate_spec

# Keep the subpackage surface explicit for readers and tooling.
__all__ = ["build_caveman_spec", "build_pirate_spec"]
