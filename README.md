# Zetra agent template

This repository owns the canonical starter tree bundled by the Zetra SDK. It contains a standard Google ADK `LlmAgent`, one approved document tool, packaged instructions, and tests. There is no second generated template or Copier dependency.

```sh
python3 scripts/render.py /path/to/my-reader --name my-reader
cd /path/to/my-reader
uv sync --locked
just validate
```

Names contain at most 48 lowercase letters, digits, and single hyphen or underscore separators. Python imports replace hyphens with underscores; distribution names replace underscores with hyphens. The renderer refuses an existing destination. It updates the project name in the lockfile as well as package paths and metadata.

For template development, use Python 3.12 and `uv sync --group dev`, then `uv run pytest` and `uv run ruff check .`. Keep the SDK Git revision and `template/uv.lock` synchronized. A checkout imported through `PYTHONPATH` is a unit development check, not installed qualification. The fixture model runs deterministic trusted host code; it is not inference or isolation evidence.
