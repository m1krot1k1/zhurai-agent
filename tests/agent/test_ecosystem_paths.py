"""Tests for agent.ecosystem_paths."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent.ecosystem_paths import (
    get_ecosystem_agents_dir,
    get_ecosystem_root,
    get_ecosystem_skills_dir,
)


def test_get_ecosystem_root_from_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    eco = tmp_path / "zhur"
    (eco / "agents").mkdir(parents=True)
    monkeypatch.setenv("ZHUR_AI_AGENT_ROOT", str(eco))

    assert get_ecosystem_root() == eco.resolve()


def test_get_ecosystem_skills_dir_when_present(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    eco = tmp_path / "zhur"
    skills = eco / "skills" / "demo"
    skills.mkdir(parents=True)
    monkeypatch.setenv("ZHUR_AI_AGENT_ROOT", str(eco))

    assert get_ecosystem_skills_dir() == (eco / "skills").resolve()


def test_get_ecosystem_agents_dir_none_without_root(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ZHUR_AI_AGENT_ROOT", raising=False)
    monkeypatch.setattr(
        "agent.ecosystem_paths._INSTALL_ROOT",
        Path("/nonexistent/install/root"),
    )

    assert get_ecosystem_root() is None
    assert get_ecosystem_agents_dir() is None
