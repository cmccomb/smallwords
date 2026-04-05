"""Fail when Python files are missing docstrings or inline comments."""

from __future__ import annotations

import ast
import io
import tokenize
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET_DIRS = ("src", "examples", "tests", "scripts")
IGNORED_COMMENT_PREFIXES = ("fmt:", "noqa", "nosec", "pragma:", "type:")


def iter_python_files() -> list[Path]:
    """Return the Python files that must satisfy the documentation policy."""
    paths: list[Path] = []
    for directory in TARGET_DIRS:
        # The policy intentionally covers tests and helper scripts too.
        paths.extend(sorted((ROOT / directory).rglob("*.py")))
    return paths


def missing_docstrings(path: Path) -> list[str]:
    """Collect missing module, class, and function docstrings for a file."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    issues: list[str] = []

    if ast.get_docstring(tree) is None:
        issues.append("missing module docstring")

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if ast.get_docstring(node) is None:
                issues.append(f"missing class docstring: {node.name} (line {node.lineno})")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if ast.get_docstring(node) is None:
                issues.append(f"missing function docstring: {node.name} (line {node.lineno})")

    return issues


def has_meaningful_comment(path: Path) -> bool:
    """Return True when a file contains at least one substantive inline comment."""
    text = path.read_text(encoding="utf-8")
    for token in tokenize.generate_tokens(io.StringIO(text).readline):
        if token.type != tokenize.COMMENT:
            continue
        content = token.string.lstrip("#").strip()
        if content and not content.startswith(IGNORED_COMMENT_PREFIXES):
            return True
    return False


def main() -> int:
    """Run the documentation policy checks and print any violations."""
    errors: list[str] = []

    for path in iter_python_files():
        for issue in missing_docstrings(path):
            errors.append(f"{path.relative_to(ROOT)}: {issue}")
        if not has_meaningful_comment(path):
            errors.append(f"{path.relative_to(ROOT)}: missing inline comment")

    if errors:
        print("Documentation policy violations:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Documentation policy checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
