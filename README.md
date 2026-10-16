# zetra-template

A [Copier](https://github.com/copier-org/copier) template for scaffolding a new
Zetra zero-trust agent in Python.

## What you get

- **[uv](https://docs.astral.sh/uv/)** for dependency management, locking and builds (`src/` layout)
- **[mise](https://mise.jdx.dev/)** pinning the Python and uv runtimes, plus task runner
- **[ruff](https://docs.astral.sh/ruff/)** for linting and formatting
- **[ty](https://docs.astral.sh/ty/)** for type checking
- **[pre-commit](https://pre-commit.com/)** hooks wiring the above together
- **[pytest](https://docs.pytest.org/)** with a starter test suite
- A minimal deny-by-default `Agent` / `Policy` skeleton
- Optional GitHub Actions CI workflow

## Usage

```bash
# from a local checkout
copier copy path/to/zetra-template my-agent

# or from git
copier copy gh:<org>/zetra-template my-agent

cd my-agent
mise trust && mise install
mise run setup
mise run check
```

### Updating an existing project

Generated projects record their answers in `.copier-answers.yml`, so once this
template lives in git (with tagged releases) you can pull in template changes:

```bash
cd my-agent
copier update
```

## Questions

| Question                 | Default                         |
| ------------------------ | ------------------------------- |
| `project_name`           | `Zetra Agent`                   |
| `project_slug`           | derived from `project_name`     |
| `package_name`           | derived from `project_slug`     |
| `description`            | `A zero-trust agent.`           |
| `author_name`            | —                               |
| `author_email`           | —                               |
| `python_version`         | `3.14` (also `3.13`, `3.12`)    |
| `include_github_actions` | `true`                          |

## Developing the template

The template files live in [`template/`](template/); `copier.yml` defines the
questions. To render the template with defaults into a temp dir and run the
generated project's full check suite:

```bash
mise run test
```
