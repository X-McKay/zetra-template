"""Contract checks for the canonical tree and standalone renderer."""

import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_render_has_indexed_agent_and_resources(tmp_path):
    target = tmp_path / "project"
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/render.py"), str(target), "--name", "my-reader"],
        check=True,
    )
    project = tomllib.loads((target / "pyproject.toml").read_text())
    assert project["project"]["name"] == "my-reader"
    assert (
        project["tool"]["zetra"]["agents"]["document_reader"]
        == "src/my_reader/agents/document_reader/agent.yaml"
    )
    assert (target / "src/my_reader/agents/document_reader/instructions/base.md").is_file()
    assert (
        "my_reader.agents.document_reader.factory:create_agent"
        in (target / project["tool"]["zetra"]["agents"]["document_reader"]).read_text()
    )
    assert not list(target.rglob("*.jinja"))


def test_renderer_rejects_invalid_names(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/render.py"),
            str(tmp_path / "project"),
            "--name",
            "../oops",
        ],
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert not (tmp_path / "project").exists()


def test_canonical_tree_has_only_standard_adk_agent():
    source = ROOT / "template/src/agent_package"
    text = "\n".join(p.read_text() for p in source.rglob("*.py"))
    assert "LlmAgent(" in text
    assert "class Agent" not in text
    assert "class Policy" not in text
    assert not list((ROOT / "template").rglob("*.jinja"))


def test_render_updates_lock_root_identity(tmp_path):
    target = tmp_path / "project"
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/render.py"), str(target), "--name", "my-reader"],
        check=True,
    )
    lock = tomllib.loads((target / "uv.lock").read_text())
    root = next(p for p in lock["package"] if p["name"] == "my-reader")
    assert root["source"] == {"editable": "."}
    assert "agent-package" not in (target / "uv.lock").read_text()


def test_render_accepts_hyphen_and_underscore_names(tmp_path):
    for name in ("my-reader", "my_reader"):
        target = tmp_path / name
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/render.py"), str(target), "--name", name],
            check=True,
        )
        project = tomllib.loads((target / "pyproject.toml").read_text())
        assert project["project"]["name"] == "my-reader"
        assert (target / "src/my_reader/agents/document_reader/factory.py").is_file()
        lock = tomllib.loads((target / "uv.lock").read_text())
        assert any(p["name"] == "my-reader" for p in lock["package"])
