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


def test_wheel_checker_rejects_missing_packaged_resources(tmp_path):
    from zipfile import ZipFile

    wheel = tmp_path / "agent_package-0.1.0-py3-none-any.whl"
    with ZipFile(wheel, "w") as archive:
        archive.writestr("agent_package/__init__.py", "")
    result = subprocess.run(
        [sys.executable, str(ROOT / "template/tests/packaging/check_wheel.py"), str(wheel)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "agent.yaml" in result.stderr


def test_wheel_checker_verifies_exact_resource_bytes(tmp_path):
    from zipfile import ZipFile

    source = ROOT / "template/src"
    resources = (
        "agent_package/agents/document_reader/agent.yaml",
        "agent_package/agents/document_reader/instructions/base.md",
    )
    wheel = tmp_path / "agent_package-0.1.0-py3-none-any.whl"
    command = [sys.executable, str(ROOT / "template/tests/packaging/check_wheel.py"), str(wheel)]
    with ZipFile(wheel, "w") as archive:
        dependency = tomllib.loads((ROOT / "template/pyproject.toml").read_text())["project"][
            "dependencies"
        ][0]
        archive.writestr("agent_package-0.1.0.dist-info/METADATA", f"Requires-Dist: {dependency}\n")
        for resource in resources:
            archive.writestr(resource, (source / resource).read_bytes())
    subprocess.run(command, check=True)
    with ZipFile(wheel, "w") as archive:
        dependency = tomllib.loads((ROOT / "template/pyproject.toml").read_text())["project"][
            "dependencies"
        ][0]
        archive.writestr("agent_package-0.1.0.dist-info/METADATA", f"Requires-Dist: {dependency}\n")
        for resource in resources:
            archive.writestr(resource, b"unexpected data")
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    assert result.returncode != 0
    assert "differs from source" in result.stderr


def renderer_module():
    import importlib.util

    spec = importlib.util.spec_from_file_location("canonical_renderer", ROOT / "scripts/render.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_renderer_rejects_collisions_and_keywords(tmp_path):
    import pytest

    for name in (
        "zetra",
        "pytest",
        "httpx",
        "google",
        "yaml",
        "class",
        "async",
        "json",
        "pydantic",
    ):
        with pytest.raises(ValueError, match="reserved"):
            renderer_module().render(tmp_path / name, name)
        assert not (tmp_path / name).exists()


def test_renderer_failure_leaves_no_destination_or_staging(tmp_path):
    import pytest

    source = tmp_path / "source"
    source.mkdir()
    (source / "a.txt").write_text("valid", encoding="utf-8")
    (source / "b.txt").write_bytes(b"\xff")
    with pytest.raises(UnicodeError):
        renderer_module().render(tmp_path / "result", "reader", source=source)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["source"]


def test_renderer_preserves_existing_destination(tmp_path):
    import pytest

    target = tmp_path / "existing"
    target.mkdir()
    (target / "keep").write_text("untouched", encoding="utf-8")
    with pytest.raises(ValueError):
        renderer_module().render(target, "reader")
    assert (target / "keep").read_text(encoding="utf-8") == "untouched"


def test_wheel_checker_rejects_unpinned_dependency_metadata(tmp_path):
    from zipfile import ZipFile

    wheel = tmp_path / "agent_package-0.1.0-py3-none-any.whl"
    source = ROOT / "template/src"
    with ZipFile(wheel, "w") as archive:
        for resource in (
            "agent_package/agents/document_reader/agent.yaml",
            "agent_package/agents/document_reader/instructions/base.md",
        ):
            archive.writestr(resource, (source / resource).read_bytes())
        archive.writestr("agent_package-0.1.0.dist-info/METADATA", "Requires-Dist: zetra==0.1.0\n")
    result = subprocess.run(
        [sys.executable, str(ROOT / "template/tests/packaging/check_wheel.py"), str(wheel)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "dependency metadata differs" in result.stderr


def test_renderer_cleans_partial_publication(tmp_path, monkeypatch):
    import pytest

    source = tmp_path / "source"
    source.mkdir()
    (source / "a.txt").write_text("café", encoding="utf-8")
    (source / "b.txt").write_text("second", encoding="utf-8")
    rename = Path.rename

    def fail_second(path, target):
        if path.name == "b.txt":
            raise OSError("injected publication failure")
        return rename(path, target)

    monkeypatch.setattr(Path, "rename", fail_second)
    with pytest.raises(OSError, match="injected"):
        renderer_module().render(tmp_path / "result", "reader", source=source)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["source"]


def test_renderer_uses_utf8(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.txt").write_text("café — agent-package", encoding="utf-8")
    renderer_module().render(tmp_path / "result", "reader", source=source)
    assert (tmp_path / "result/a.txt").read_bytes() == "café — reader".encode()
