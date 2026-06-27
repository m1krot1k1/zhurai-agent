"""Tests for agent.ecosystem_delegate."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent.ecosystem_delegate import (
    build_delegate_branch_context,
    list_ecosystem_agent_ids,
    resolve_agent_brief,
)


def test_resolve_agent_brief_from_agents_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    eco = tmp_path / "zhur"
    brief = eco / "agents" / "code.md"
    brief.parent.mkdir(parents=True)
    brief.write_text("---\nname: code\n---\n", encoding="utf-8")
    monkeypatch.setenv("ZHUR_AI_AGENT_ROOT", str(eco))

    assert resolve_agent_brief("code") == brief.resolve()


def test_build_delegate_branch_context_includes_brief_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    eco = tmp_path / "zhur"
    brief = eco / "agents" / "code.md"
    brief.parent.mkdir(parents=True)
    brief.write_text("---\nname: code\n---\n# Code agent\nImplement in Python.\n", encoding="utf-8")
    monkeypatch.setenv("ZHUR_AI_AGENT_ROOT", str(eco))

    ctx = build_delegate_branch_context(
        "code",
        objective="Implement feature X",
        original_request="сделай feature X",
        ownership="src/feature/**",
    )
    assert "AGENT_BRIEF:" in ctx
    assert "# Code agent" in ctx
    assert "Implement in Python." in ctx
    assert "AGENT_BRIEF_PATH:" not in ctx
    assert "ORIGINAL_REQUEST: сделай feature X" in ctx
    assert "OWNERSHIP: src/feature/**" in ctx


def test_list_ecosystem_agent_ids_excludes_readme(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    eco = tmp_path / "zhur"
    agents = eco / "agents"
    agents.mkdir(parents=True)
    (agents / "code.md").write_text("x", encoding="utf-8")
    (agents / "README.md").write_text("x", encoding="utf-8")
    monkeypatch.setenv("ZHUR_AI_AGENT_ROOT", str(eco))

    assert list_ecosystem_agent_ids() == ["code"]
