"""Render the canonical SDK-compatible tree using only the standard library."""

import argparse
import re
from pathlib import Path


def render(destination: Path, name: str) -> None:
    if len(name) > 48 or not re.fullmatch(r"[a-z][a-z0-9]*(?:[-_][a-z0-9]+)*", name):
        raise ValueError(
            "name must be at most 48 characters: lowercase words separated by hyphens or underscores"
        )
    if destination.exists():
        raise ValueError("destination already exists")
    source = Path(__file__).resolve().parents[1] / "template"
    package = name.replace("-", "_")
    distribution = name.replace("_", "-")
    destination.mkdir(parents=True)
    for item in sorted(source.rglob("*")):
        if not item.is_file() or any(
            p in {"__pycache__", ".pytest_cache", ".venv", ".ruff_cache", "dist"}
            for p in item.relative_to(source).parts
        ):
            continue
        relative = str(item.relative_to(source)).replace("agent_package", package)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        text = (
            item.read_text()
            .replace("agent_package", package)
            .replace("agent-package", distribution)
        )
        target.write_text(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    try:
        render(args.path, args.name)
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
