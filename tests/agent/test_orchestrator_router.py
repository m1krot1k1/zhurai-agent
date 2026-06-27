"""Tests for agent.orchestrator_router."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agent.orchestrator_router import (
    build_orchestration_injection,
    build_orchestrator_recon_injection,
    build_root_synthesis_injection,
    classify_complexity,
    enrich_delegate_task_entry,
    extract_original_request,
    infer_agent_id_from_text,
    is_ecosystem_orchestrator_subagent,
    is_start_router_turn,
    orchestrate_mode,
    parse_agent_id_from_envelope,
    plan_parallel_delegate_tasks,
    should_auto_orchestrate,
    should_programmatic_orchestrate,
    suggest_specialists,
    try_orchestrator_child_fanout,
    try_orchestrator_post_recon_fanout,
    try_programmatic_orchestration,
    try_programmatic_start_router,
    try_start_child_handoff,
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


def test_is_start_router_turn() -> None:
    assert is_start_router_turn("/start analyze repo") is True
    assert is_start_router_turn("/start — router mode. delegate...") is True
    assert is_start_router_turn("analyze repo only") is False


def test_try_programmatic_start_router_dispatches_start_agent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    eco = tmp_path / "zhur"
    (eco / "agents").mkdir(parents=True)
    (eco / "agents" / "start.md").write_text("x", encoding="utf-8")
    (eco / "agents" / "orchestrator.md").write_text("x", encoding="utf-8")
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
    agent._delegate_branch_context = ""
    agent.valid_tool_names = {"delegate_task"}
    agent.session_id = "sess-root"
    agent._dispatch_delegate_task.return_value = json.dumps(
        {"status": "dispatched", "count": 1}
    )

    msg = (
        "/start полный анализ репозитория: architecture, git history, security audit "
        "и проверка multi-agent swarm orchestration."
    )
    response = try_programmatic_orchestration(agent, msg, task_id="task-root")
    assert response is not None
    assert "start" in response.lower()
    agent._dispatch_delegate_task.assert_called_once()
    call = agent._dispatch_delegate_task.call_args[0][0]
    assert "tasks" not in call or call.get("tasks") is None
    assert "AGENT_ID: start" in (call.get("context") or "")
    assert call.get("background") is True


def test_try_start_child_handoff_dispatches_orchestrator(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    eco = tmp_path / "zhur"
    (eco / "agents").mkdir(parents=True)
    (eco / "agents" / "start.md").write_text("x", encoding="utf-8")
    (eco / "agents" / "orchestrator.md").write_text("x", encoding="utf-8")
    monkeypatch.setenv("ZHUR_AI_AGENT_ROOT", str(eco))

    agent = MagicMock()
    agent._start_handoff_done = False
    agent.valid_tool_names = {"delegate_task"}
    agent.session_id = "sess-start"
    agent._delegate_branch_context = (
        "AGENT_ID: start\nORIGINAL_REQUEST: analyze repo architecture and security"
    )
    agent._dispatch_delegate_task.return_value = json.dumps(
        {"status": "dispatched", "count": 1}
    )

    response = try_start_child_handoff(agent, "continue", task_id="task-start")
    assert response is not None
    assert "orchestrator" in response.lower()
    call = agent._dispatch_delegate_task.call_args[0][0]
    assert "AGENT_ID: orchestrator" in (call.get("context") or "")
    assert call.get("role") == "orchestrator"
    assert agent._start_handoff_done is True


def test_try_programmatic_start_router_no_fallthrough_on_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    eco = tmp_path / "zhur"
    (eco / "agents").mkdir(parents=True)
    (eco / "agents" / "start.md").write_text("x", encoding="utf-8")
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
    agent.valid_tool_names = {"delegate_task"}
    agent.session_id = "sess-root"
    agent._dispatch_delegate_task.return_value = json.dumps({"error": "spawn paused"})

    msg = "/start полный анализ репозитория и security audit"
    response = try_programmatic_orchestration(agent, msg, task_id="task-root")
    assert response is not None
    assert "start" in response.lower()
    assert "repo-explorer" not in response
    call = agent._dispatch_delegate_task.call_args[0][0]
    assert "tasks" not in call or not call.get("tasks")


def test_build_orchestration_injection_start_router_hint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "agent.orchestrator_router._load_delegation_cfg",
        lambda: {"auto_orchestrate": True, "auto_orchestrate_mode": "both"},
    )
    msg = "/start analyze repo architecture and security"
    injection = build_orchestration_injection(msg)
    assert injection is not None
    assert "AGENT_ID:start" in injection
    assert "leaf specialists" in injection.lower()


def test_build_orchestration_injection_skips_start_in_programmatic_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "agent.orchestrator_router._load_delegation_cfg",
        lambda: {"auto_orchestrate": True, "auto_orchestrate_mode": "programmatic"},
    )
    msg = "/start analyze repo architecture and security"
    assert build_orchestration_injection(msg) is None


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
        lambda: {
            "auto_orchestrate": True,
            "auto_orchestrate_min_tasks": 2,
            "orchestrator_two_phase": False,
        },
    )

    agent = MagicMock()
    agent._delegate_role = "orchestrator"
    agent._orchestrator_fanout_done = False
    agent.valid_tool_names = {"delegate_task"}
    agent.session_id = "sess-orch"
    agent._delegate_branch_context = (
        "AGENT_ID: orchestrator\n"
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


def test_try_orchestrator_child_fanout_skips_specialist_agent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "agent.orchestrator_router._load_delegation_cfg",
        lambda: {"auto_orchestrate": True, "auto_orchestrate_min_tasks": 2},
    )
    agent = MagicMock()
    agent._delegate_role = "orchestrator"
    agent._orchestrator_fanout_done = False
    agent.valid_tool_names = {"delegate_task"}
    agent._delegate_branch_context = (
        "AGENT_ID: repo-explorer\nORIGINAL_REQUEST: map the repo\n"
    )
    response = try_orchestrator_child_fanout(agent, "Coordinate", task_id="t1")
    assert response is None
    agent._dispatch_delegate_task.assert_not_called()


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


def test_try_programmatic_orchestration_skips_async_delegation_reinjection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
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
    agent.valid_tool_names = {"delegate_task"}

    msg = (
        "[ASYNC DELEGATION BATCH COMPLETE — deleg_abc]\n"
        "ORIGINAL_REQUEST: Analyze repo architecture and security\n"
        "TASK 1/5: repo-explorer ..."
    )
    assert try_programmatic_orchestration(agent, msg, task_id="task-1") is None
    agent._dispatch_delegate_task.assert_not_called()


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


def test_try_orchestrator_child_fanout_skips_when_two_phase_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "agent.orchestrator_router._load_delegation_cfg",
        lambda: {"auto_orchestrate": True, "orchestrator_two_phase": True},
    )
    agent = MagicMock()
    agent._delegate_role = "orchestrator"
    agent._delegate_branch_context = (
        "AGENT_ID: orchestrator\nORIGINAL_REQUEST: analyze repo\n"
    )
    agent.valid_tool_names = {"delegate_task"}
    assert try_orchestrator_child_fanout(agent, "Coordinate", task_id="t1") is None
    agent._dispatch_delegate_task.assert_not_called()


def test_build_orchestrator_recon_injection_for_ecosystem_orchestrator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "agent.orchestrator_router._load_delegation_cfg",
        lambda: {"orchestrator_two_phase": True},
    )
    agent = MagicMock()
    agent._delegate_role = "orchestrator"
    agent._orchestrator_fanout_done = False
    agent._delegate_branch_context = (
        "AGENT_ID: orchestrator\nORIGINAL_REQUEST: map architecture and security\n"
    )
    injection = build_orchestrator_recon_injection(agent, "Coordinate user request")
    assert injection is not None
    assert "PHASE 1" in injection
    assert "PHASE 2" in injection
    assert "map architecture and security" in injection


def test_build_orchestrator_recon_injection_skips_after_fanout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "agent.orchestrator_router._load_delegation_cfg",
        lambda: {"orchestrator_two_phase": True},
    )
    agent = MagicMock()
    agent._delegate_role = "orchestrator"
    agent._orchestrator_fanout_done = True
    agent._delegate_branch_context = "AGENT_ID: orchestrator\nORIGINAL_REQUEST: x\n"
    assert build_orchestrator_recon_injection(agent, "x") is None


def test_try_orchestrator_post_recon_fanout_dispatches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    eco = tmp_path / "zhur"
    (eco / "agents").mkdir(parents=True)
    (eco / "agents" / "code.md").write_text("x", encoding="utf-8")
    (eco / "agents" / "repo-explorer.md").write_text("x", encoding="utf-8")
    monkeypatch.setenv("ZHUR_AI_AGENT_ROOT", str(eco))
    monkeypatch.setattr(
        "agent.orchestrator_router._load_delegation_cfg",
        lambda: {
            "auto_orchestrate": True,
            "auto_orchestrate_min_tasks": 2,
            "orchestrator_two_phase": True,
        },
    )

    agent = MagicMock()
    agent._delegate_role = "orchestrator"
    agent._orchestrator_fanout_done = False
    agent.session_id = "sess-orch"
    agent._delegate_branch_context = (
        "AGENT_ID: orchestrator\n"
        "ORIGINAL_REQUEST: Analyze repo architecture and security audit\n"
    )
    agent._dispatch_delegate_task.return_value = json.dumps(
        {"status": "dispatched", "count": 2}
    )

    messages = [
        {"role": "assistant", "content": "Found src/ and tests/; need explorer + security."},
        {"role": "tool", "name": "read_file", "content": '{"path": "run_agent.py"}'},
    ]

    with patch(
        "agent.orchestrator_router._plan_tasks_from_recon",
        return_value=[
            {"goal": "Map repo", "context": "AGENT_ID: repo-explorer\n", "role": "leaf"},
            {"goal": "Security audit", "context": "AGENT_ID: security-auditor\n", "role": "leaf"},
        ],
    ):
        response = try_orchestrator_post_recon_fanout(
            agent,
            messages,
            "Coordinate user request",
            task_id="task-orch",
        )

    assert response is not None
    agent._dispatch_delegate_task.assert_called_once()
    assert agent._orchestrator_fanout_done is True


def test_try_orchestrator_post_recon_skips_when_delegate_already_called(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "agent.orchestrator_router._load_delegation_cfg",
        lambda: {"orchestrator_two_phase": True, "auto_orchestrate_min_tasks": 2},
    )
    agent = MagicMock()
    agent._delegate_role = "orchestrator"
    agent._orchestrator_fanout_done = False
    agent._delegate_branch_context = (
        "AGENT_ID: orchestrator\nORIGINAL_REQUEST: analyze repo\n"
    )
    messages = [
        {
            "role": "tool",
            "name": "delegate_task",
            "content": '{"status": "dispatched", "count": 2}',
        },
    ]
    assert (
        try_orchestrator_post_recon_fanout(agent, messages, "x", task_id="t1") is None
    )
    assert agent._orchestrator_fanout_done is True
    agent._dispatch_delegate_task.assert_not_called()


def test_is_ecosystem_orchestrator_subagent() -> None:
    orch = MagicMock()
    orch._delegate_role = "orchestrator"
    orch._delegate_branch_context = "AGENT_ID: orchestrator\nORIGINAL_REQUEST: x\n"
    assert is_ecosystem_orchestrator_subagent(orch) is True

    leaf = MagicMock()
    leaf._delegate_role = "orchestrator"
    leaf._delegate_branch_context = "AGENT_ID: code\nORIGINAL_REQUEST: x\n"
    assert is_ecosystem_orchestrator_subagent(leaf) is False


def test_build_root_synthesis_injection_batch_complete() -> None:
    msg = (
        "[ASYNC DELEGATION BATCH COMPLETE — deleg_xyz]\n"
        "ORIGINAL_REQUEST: full repo analysis\n"
        "TASK 1/2: repo-explorer ..."
    )
    injection = build_root_synthesis_injection(msg)
    assert injection is not None
    assert "SYNTHESIS" in injection
    assert "full repo analysis" in injection
    assert "Do NOT call delegate_task" in injection
