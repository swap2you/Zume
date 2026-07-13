import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parents[1]


@pytest.fixture()
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture()
def tmp_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolated Zume root with real config and examples, used as cwd."""
    shutil.copytree(REPO_ROOT / "config", tmp_path / "config")
    shutil.copytree(REPO_ROOT / "examples", tmp_path / "examples")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='zume-test'\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture()
def theme(repo_root: Path) -> dict:
    from zume.config import load_theme

    return load_theme(repo_root)
