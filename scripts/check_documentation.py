"""Fail when Python files are missing docstrings or inline comments."""

from __future__ import annotations

import ast
import io
import tokenize
from pathlib import Path

# The repository root anchors the documentation policy scan.
ROOT = Path(__file__).resolve().parents[1]
# These directories make up the maintained Python surface of the project.
TARGET_DIRS = ("src", "examples", "tests", "scripts")
# Tooling-only comments do not count toward the inline comment requirement.
IGNORED_COMMENT_PREFIXES = ("fmt:", "noqa", "nosec", "pragma:", "type:")
# Library code and repo scripts must use sectioned function docstrings.
STRUCTURED_DOCSTRING_DIRS = (("src", "smallwords"), ("scripts",))


def iter_python_files() -> list[Path]:
    """Return the Python files that must satisfy the documentation policy.

    Returns:
        The Python files covered by the repository documentation policy.
    """
    paths: list[Path] = []
    for directory in TARGET_DIRS:
        # The policy intentionally covers tests and helper scripts too.
        paths.extend(sorted((ROOT / directory).rglob("*.py")))
    return paths


def missing_docstrings(path: Path) -> list[str]:
    """Collect missing module, class, and function docstrings for a file.

    Args:
        path: Python file to inspect.

    Returns:
        Human-readable docstring violations for the file.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    issues: list[str] = []

    if ast.get_docstring(tree) is None:
        issues.append("missing module docstring")

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if ast.get_docstring(node) is None:
                issues.append(
                    f"missing class docstring: {node.name} (line {node.lineno})"
                )
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if ast.get_docstring(node) is None:
                issues.append(
                    f"missing function docstring: {node.name} (line {node.lineno})"
                )

    return issues


def _relative_parts(path: Path) -> tuple[str, ...]:
    """Return the path parts relative to the repository root.

    Args:
        path: Python file to normalize.

    Returns:
        The path parts relative to the repository root.
    """
    return path.relative_to(ROOT).parts


def _requires_structured_docstrings(path: Path) -> bool:
    """Return whether a file must use sectioned function docstrings.

    Args:
        path: Python file to inspect.

    Returns:
        True when the file lives in a directory that requires sectioned docstrings.
    """
    parts = _relative_parts(path)
    return any(parts[: len(prefix)] == prefix for prefix in STRUCTURED_DOCSTRING_DIRS)


def _function_argument_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """Return the meaningful argument names for one function definition.

    Args:
        node: Function definition node to inspect.

    Returns:
        The argument names that should appear in an ``Args:`` section.
    """
    positional = [arg.arg for arg in (*node.args.posonlyargs, *node.args.args)]
    keyword_only = [arg.arg for arg in node.args.kwonlyargs]
    if node.args.vararg is not None:
        positional.append(node.args.vararg.arg)
    if node.args.kwarg is not None:
        keyword_only.append(node.args.kwarg.arg)
    return [
        name for name in (*positional, *keyword_only) if name not in {"self", "cls"}
    ]


def _returns_value(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return whether a function annotation advertises a non-``None`` return.

    Args:
        node: Function definition node to inspect.

    Returns:
        True when the function annotation indicates a return value.
    """
    annotation = node.returns
    if annotation is None:
        return False
    if isinstance(annotation, ast.Constant) and annotation.value is None:
        return False
    if isinstance(annotation, ast.Name) and annotation.id == "None":
        return False
    return True


def structured_docstring_issues(path: Path) -> list[str]:
    """Collect missing structured-docstring sections for one Python file.

    Args:
        path: Python file to inspect.

    Returns:
        Human-readable structured docstring violations for the file.
    """
    if not _requires_structured_docstrings(path):
        return []

    tree = ast.parse(path.read_text(encoding="utf-8"))
    issues: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        docstring = ast.get_docstring(node)
        if docstring is None:
            continue

        argument_names = _function_argument_names(node)
        if argument_names and "Args:" not in docstring:
            issues.append(f"missing Args section: {node.name} (line {node.lineno})")
        if _returns_value(node) and "Returns:" not in docstring:
            issues.append(f"missing Returns section: {node.name} (line {node.lineno})")

    return issues


def has_meaningful_comment(path: Path) -> bool:
    """Return True when a file contains at least one substantive inline comment.

    Args:
        path: Python file to inspect.

    Returns:
        True when the file contains a substantive inline comment.
    """
    text = path.read_text(encoding="utf-8")
    for token in tokenize.generate_tokens(io.StringIO(text).readline):
        if token.type != tokenize.COMMENT:
            continue
        content = token.string.lstrip("#").strip()
        if content and not content.startswith(IGNORED_COMMENT_PREFIXES):
            return True
    return False


def _has_leading_comment(lines: list[str], lineno: int) -> bool:
    """Return whether a constant definition has a nearby leading comment.

    Args:
        lines: Source file lines.
        lineno: 1-based line number of the constant definition.

    Returns:
        True when the closest preceding non-empty line is a comment.
    """
    index = lineno - 2
    while index >= 0 and not lines[index].strip():
        index -= 1
    return index >= 0 and lines[index].lstrip().startswith("#")


def constant_comment_issues(path: Path) -> list[str]:
    """Collect uppercase constants that are missing an introducing comment.

    Args:
        path: Python file to inspect.

    Returns:
        Human-readable constant-comment violations for the file.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    tree = ast.parse("\n".join(lines))
    issues: list[str] = []

    for node in tree.body:
        targets: list[str] = []
        if isinstance(node, ast.Assign):
            targets = [
                target.id for target in node.targets if isinstance(target, ast.Name)
            ]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            targets = [node.target.id]

        for name in targets:
            if not name.isupper():
                continue
            if not _has_leading_comment(lines, node.lineno):
                issues.append(f"missing constant comment: {name} (line {node.lineno})")

    return issues


def main() -> int:
    """Run the documentation policy checks and print any violations.

    Returns:
        Process exit code for the documentation policy run.
    """
    errors: list[str] = []

    for path in iter_python_files():
        for issue in missing_docstrings(path):
            errors.append(f"{path.relative_to(ROOT)}: {issue}")
        for issue in structured_docstring_issues(path):
            errors.append(f"{path.relative_to(ROOT)}: {issue}")
        for issue in constant_comment_issues(path):
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
