"""Tests for agent.orchestrator_router."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agent.orchestrator_router import (
    build_orchestration_injection,
    classify_complexity,
    orchestrate_mode,
    parse_agent_id_from_envelope,
    plan_parallel_delegate_tasks,
    should_auto_orchestrate,
    should_programmatic_orchestrate,
    suggest_specialists,
    try_programmatic_orchestration,
)


def test_classify_trivial_greeting() -> None:
    assert classify_complexity("привет!") == "trivial"
    assert classify_complexity("hello") == "trivial"


def test_classify_multi_long_request() -> None:
    msg = (
        "Проанализируй репозиторий zhur.ai-agent: найди архитектуру delegate_task, "
        "исправь баг с max_spawn_depth, напиши тесты и сделай security review."
    )
    assert classify_complexity(msg) == "multi"


def test_suggest_specialists_for_repo_analysis() -> None:
    msg = "Analyze the codebase structure and review security vulnerabilities"
    ids = suggest_specialists(msg)
    assert "repo-explorer" in ids
    assert "security-auditor" in ids


def test_parse_agent_id_from_envelope() -> None:
    ctx = "OBJECTIVE: scan\nAGENT_ID: code-reviewer\nOWNERSHIP: src/"
    assert parse_agent_id_from_envelope(ctx) == "code-reviewer"


def test_plan_parallel_delegate_tasks_includes_agent_ids(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    eco = tmp_path / "zhur"
    (eco / "agents").mkdir(parents=True)
    (eco / "agents" / "code.md").write_text("---\nname: code\n---\n", encoding="utf-8")
    (eco / "agents" / "repo-explorer.md").write_text("---\nname: repo-explorer\n---\n", encoding="utf-8")
    monkeypatch.setenv("ZHUR_AI_AGENT_ROOT", str(eco))

    msg = (
        "Сделай полный анализ репозитория: architecture, bugs, tests, security audit "
        "и предложи план исправлений для multi-agent orchestration."
    )
    tasks = plan_parallel_delegate_tasks(msg)
    assert len(tasks) >= 2
    for task in tasks:
        assert task.get("goal")
        assert "AGENT_ID:" in (task.get("context") or "")
        assert task.get("role") == "leaf"


def test_build_orchestration_injection_disabled_in_programmatic_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    eco = tmp_path / "zhur"
    (eco / "agents").mkdir(parents=True)
    monkeypatch.setenv("ZHUR_AI_AGENT_ROOT", str(eco))
    monkeypatch.setattr(
        "agent.orchestrator_router._load_delegation_cfg",
        lambda: {"auto_orchestrate": True, "auto_orchestrate_mode": "programmatic"},
    )
    msg = "Implement feature X and write tests and update docs for the whole repo"
    assert orchestrate_mode() == "programmatic"
    assert should_programmatic_orchestrate(msg) is True
    assert should_auto_orchestrate(msg) is False
    assert build_orchestration_injection(msg) is None


def test_build_orchestration_injection_hint_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    eco = tmp_path / "zhur"
    (eco / "agents").mkdir(parents=True)
    monkeypatch.setenv("ZHUR_AI_AGENT_ROOT", str(eco))
    monkeypatch.setattr(
        "agent.orchestrator_router._load_delegation_cfg",
        lambda: {"auto_orchestrate": True, "auto_orchestrate_mode": "hint"},
    )
    msg = (
        "Сделай полный анализ репозитория: architecture, bugs, tests, security audit "
        "и предложи план исправлений."
    )
    injection = build_orchestration_injection(msg)
    assert injection is not None
    assert 'role="orchestrator"' in injection


def test_try_programmatic_orchestration_dispatches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    eco = tmp_path / "zhur"
    (eco / "agents").mkdir(parents=True)
    (eco / "agents" / "code.md").write_text("x", encoding="utf-8")
    monkeypatch.setenv("ZHUR_AI_AGENT_ROOT", str(eco))
    monkeypatch.setattr(
        "agent.orchestrator_router._load_delegation_cfg",
        lambda: {
            "auto_orchestrate": True,
            "auto_orchestrate_mode": "programmatic",
            "auto_orchestrate_min_tasks": 2,
        },
    )

    agent = MagicMock()
    agent._delegate_depth = 0
    agent.valid_tool_names = {"delegate_task", "terminal", "file"}
    agent.session_id = "sess-1"
    agent._dispatch_delegate_task.return_value = json.dumps(
        {
            "status": "dispatched",
            "mode": "background",
            "count": 2,
            "delegation_id": "del-1",
            "goals": ["a", "b"],
        }
    )

    msg = (
        "Analyze the repository architecture, fix delegate_task bugs, "
        "add tests, and run a security audit."
    )
    response = try_programmatic_orchestration(agent, msg, task_id="task-1")
    assert response is not None
    assert "repo-explorer" in response or "специалист" in response.lower()
    agent._dispatch_delegate_task.assert_called_once()
    call_args = agent._dispatch_delegate_task.call_args[0][0]
    assert isinstance(call_args.get("tasks"), list)
    assert len(call_args["tasks"]) >= 2


def test_try_programmatic_skips_without_delegate_tool(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    eco = tmp_path / "zhur"
    (eco / "agents").mkdir(parents=True)
    monkeypatch.setenv("ZHUR_AI_AGENT_ROOT", str(eco))
    monkeypatch.setattr(
        "agent.orchestrator_router._load_delegation_cfg",
        lambda: {"auto_orchestrate": True, "auto_orchestrate_mode": "programmatic"},
    )

    agent = MagicMock()
    agent._delegate_depth = 0
    agent.valid_tool_names = {"terminal", "file"}

    msg = "Analyze repo and fix bugs and write tests and security review"
    assert try_programmatic_orchestration(agent, msg, task_id="t") is None
    agent._dispatch_delegate_task.assert_not_called()
