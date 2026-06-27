"""Tests for agent.orchestrator_router."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agent.orchestrator_router import (
    build_orchestration_injection,
    classify_complexity,
    enrich_delegate_task_entry,
    extract_original_request,
    infer_agent_id_from_text,
    orchestrate_mode,
    parse_agent_id_from_envelope,
    plan_parallel_delegate_tasks,
    should_auto_orchestrate,
    should_programmatic_orchestrate,
    suggest_specialists,
    try_orchestrator_child_fanout,
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


def test_classify_start_with_body_is_multi() -> None:
    msg = (
        "/start полный анализ репозитория: architecture, git history, security audit "
        "и проверка multi-agent swarm orchestration."
    )
    assert classify_complexity(msg) == "multi"
    assert classify_complexity("/start") == "trivial"


def test_infer_agent_id_from_goal_keywords() -> None:
    assert infer_agent_id_from_text("Deep code review of orchestration bugs") == "code-reviewer"
    assert infer_agent_id_from_text("Map the codebase structure and key modules") == "repo-explorer"


def test_extract_original_request() -> None:
    ctx = 'ORIGINAL_REQUEST: analyze repo\\nMODE: multi_domain'
    assert extract_original_request(ctx) == "analyze repo"


def test_enrich_delegate_task_entry_adds_agent_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    eco = tmp_path / "zhur"
    (eco / "agents").mkdir(parents=True)
    (eco / "agents" / "repo-explorer.md").write_text("---\n", encoding="utf-8")
    monkeypatch.setenv("ZHUR_AI_AGENT_ROOT", str(eco))

    enriched = enrich_delegate_task_entry(
        {"goal": "Map the codebase structure and navigation for this repository"}
    )
    assert "AGENT_ID: repo-explorer" in (enriched.get("context") or "")


def test_try_orchestrator_child_fanout_dispatches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    eco = tmp_path / "zhur"
    (eco / "agents").mkdir(parents=True)
    (eco / "agents" / "code.md").write_text("x", encoding="utf-8")
    (eco / "agents" / "repo-explorer.md").write_text("x", encoding="utf-8")
    monkeypatch.setenv("ZHUR_AI_AGENT_ROOT", str(eco))
    monkeypatch.setattr(
        "agent.orchestrator_router._load_delegation_cfg",
        lambda: {"auto_orchestrate": True, "auto_orchestrate_min_tasks": 2},
    )

    agent = MagicMock()
    agent._delegate_role = "orchestrator"
    agent._orchestrator_fanout_done = False
    agent.valid_tool_names = {"delegate_task"}
    agent.session_id = "sess-orch"
    agent._delegate_branch_context = (
        "ORIGINAL_REQUEST: Analyze repo architecture and security audit\nMODE: multi_domain"
    )
    agent._dispatch_delegate_task.return_value = json.dumps(
        {"status": "dispatched", "count": 2, "results": []}
    )

    response = try_orchestrator_child_fanout(
        agent,
        "Coordinate user request",
        task_id="task-orch",
    )
    assert response is not None
    agent._dispatch_delegate_task.assert_called_once()
    call = agent._dispatch_delegate_task.call_args[0][0]
    assert call.get("background") is True
    assert len(call.get("tasks") or []) >= 2
    assert agent._orchestrator_fanout_done is True


def test_suggest_specialists_for_repo_analysis() -> None:
    msg = "Analyze the codebase structure and review security vulnerabilities"
    ids = suggest_specialists(msg)
    assert "repo-explorer" in ids
    assert "security-auditor" in ids


def test_parse_agent_id_from_envelope() -> None:
    ctx = "OBJECTIVE: scan\nAGENT_ID: code-reviewer\nOWNERSHIP: src/"
    assert parse_agent_id_from_envelope(ctx) == "code-reviewer"
    assert (
        parse_agent_id_from_envelope("AGENT_BRIEF_PATH: /repo/agents/repo-explorer.md")
        == "repo-explorer"
    )
    assert parse_agent_id_from_envelope('Task(subagent_type="code", prompt="x")') == "code"


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
