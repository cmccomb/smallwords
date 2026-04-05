# Releasing `smallwords`

This repository is set up for PyPI Trusted Publishing through GitHub Actions.

Before the first release:

1. Create the `smallwords` project on PyPI.
2. Configure a Trusted Publisher on PyPI for this GitHub repository.
3. Add the `pypi` GitHub Actions environment if you want environment-level protection rules.

Recommended release flow:

```bash
python -m pip install -e ".[dev]"
ruff check .
ruff format --check .
pytest
python scripts/check_documentation.py
python -m build
python -m twine check --strict dist/*
python -m venv /tmp/smallwords-release-check
/tmp/smallwords-release-check/bin/python -m pip install --upgrade pip
/tmp/smallwords-release-check/bin/python -m pip install dist/*.whl
/tmp/smallwords-release-check/bin/python -c "import smallwords; print(smallwords.__version__)"
```

Then:

1. Update `version` in `pyproject.toml`.
2. Commit the release.
3. Create and push a Git tag.
4. Publish a GitHub release from that tag.

The `Publish` workflow builds the distributions, validates them with `twine`,
and uploads them to PyPI through Trusted Publishing.
