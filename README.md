# Zetra agent template

This repository owns the canonical starter tree bundled by the Zetra SDK. It contains a standard Google ADK `LlmAgent`, one approved document tool, packaged instructions, and tests. There is no second generated template or Copier dependency.

```sh
python3 scripts/render.py /path/to/my-reader --name my-reader
cd /path/to/my-reader
uv sync --locked
just validate
```

Names contain at most 48 lowercase letters, digits, and single hyphen or underscore separators. Python imports replace hyphens with underscores; distribution names replace underscores with hyphens. Python keywords, standard-library modules, locked dependency names, and dependency import namespaces are reserved. The renderer reads and writes UTF-8 and stages the tree before creating a destination; failures remove its incomplete output. It refuses an existing destination. It updates the project name in the lockfile as well as package paths and metadata.

For template development, use Python 3.12.14 and uv 0.13.1, and `uv sync --group dev`, then `uv run pytest` and `uv run ruff check .` and `uv run ruff format --check .`. Keep the SDK Git revision and `template/uv.lock` synchronized. A checkout imported through `PYTHONPATH` is a unit development check, not installed qualification. The fixture model runs deterministic trusted host code; it is not inference or isolation evidence.

Pending SDK Git pins must remain reachable from their remote repositories. Merge the prerequisite SDK PRs in order: #4, then #5, then this template PR, using merge commits only; do not squash or rebase away commits referenced by a template or wheel. Validate the final SDK pin and regenerate the lock before merging this template. This policy does not authorize merges or tags.

The wheel retains the exact SDK Git URL in its standard dependency metadata. CI checks metadata and packaged resource bytes, then installs the wheel into a fresh environment with dependency resolution enabled. The renderer reserves distribution names from the lock and maintains explicit import aliases in `scripts/render.py`; update these aliases when locked dependencies change.
