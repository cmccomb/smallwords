"""Fail when public package modules or public API objects lack docstrings."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "src" / "smallwords"


def iter_python_files() -> list[Path]:
    """Return the Python files that make up the distributed package."""
    return sorted(PACKAGE_ROOT.rglob("*.py"))


def _public_method_issues(node: ast.ClassDef) -> list[str]:
    """Collect missing docstrings for public methods on a public class."""
    issues: list[str] = []
    for child in node.body:
        if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if child.name.startswith("_"):
            continue
        if ast.get_docstring(child) is None:
            issues.append(
                f"missing public method docstring: {node.name}.{child.name} (line {child.lineno})"
            )
    return issues


def docstring_issues(path: Path) -> list[str]:
    """Collect missing public API docstrings for one package file."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    issues: list[str] = []

    if ast.get_docstring(tree) is None:
        issues.append("missing module docstring")

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            if ast.get_docstring(node) is None:
                issues.append(
                    f"missing public class docstring: {node.name} (line {node.lineno})"
                )
            issues.extend(_public_method_issues(node))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith(
            "_"
        ):
            if ast.get_docstring(node) is None:
                issues.append(
                    f"missing public function docstring: {node.name} (line {node.lineno})"
                )

    return issues


def main() -> int:
    """Check package docstring coverage and print any violations."""
    failures: list[str] = []
    for path in iter_python_files():
        issues = docstring_issues(path)
        if issues:
            relpath = path.relative_to(ROOT)
            failures.extend(f"{relpath}: {issue}" for issue in issues)

    if failures:
        for failure in failures:
            print(failure)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
