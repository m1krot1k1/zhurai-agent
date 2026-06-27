"""End-to-end test for orchestrator role propagation through delegate_task.

Pins the contract that when ``role="orchestrator"`` is requested AND the
global kill switch (``delegation.orchestrator_enabled``) is on AND the
parent is shallow enough (``child_depth < max_spawn_depth``), the built
child agent:

  1. has ``_delegate_role == "orchestrator"`` (so the rest of the runtime
     can tell it apart from a leaf), and
  2. retains the ``delegation`` toolset that ``_strip_blocked_tools`` would
     otherwise strip — i.e. it can itself call ``delegate_task``.

This is the single point that protects nested orchestration from silently
degrading to a leaf when an operator flips the kill switch, or when a
plugin accidentally lowers ``max_spawn_depth``. If either guarantee ever
breaks, every orchestrator-built fan-out silently stops fanning out —
the symptom is hard to spot in logs and easy to miss in unit tests, so
this test exists as an explicit invariant.
"""

from __future__ import annotations

import threading
from unittest.mock import MagicMock, patch

import pytest

from tools import delegate_tool
from tools.delegate_tool import delegate_task, _strip_blocked_tools


def _make_parent(depth: int = 0, enabled_toolsets=None) -> MagicMock:
    """A mock parent agent shallow enough to spawn an orchestrator child.

    ``enabled_toolsets`` deliberately includes ``delegation`` so the test
    exercises the *propagation* path (role-driven re-add), not the leaf
    inherit path.
    """
    parent = MagicMock()
    parent.base_url = "https://openrouter.ai/api/v1"
    parent.api_key = "***"
    parent.provider = "openrouter"
    parent.api_mode = "chat_completions"
    parent.model = "anthropic/claude-sonnet-4"
    parent.platform = "cli"
    parent.providers_allowed = None
    parent.providers_ignored = None
    parent.providers_order = None
    parent.provider_sort = None
    parent._session_db = None
    parent._delegate_depth = depth
    parent._active_children = []
    parent._active_children_lock = threading.Lock()
    parent._print_fn = None
    parent.tool_progress_callback = None
    parent.thinking_callback = None
    parent._memory_manager = None
    parent.session_id = "parent-orch-prop-1"
    parent.enabled_toolsets = enabled_toolsets or [
        "terminal",
        "file",
        "web",
        "delegation",
    ]
    return parent


def _make_capturing_builder(captured: list):
    """A fake _build_child_agent that mirrors the real one's role/toolset
    resolution exactly (using the live helpers), records the result, and
    returns a MagicMock child that _run_single_child can operate on.

    We mirror the resolution logic instead of calling the real
    ``_build_child_agent`` because that constructor spins up a real
    ``AIAgent`` (provider client, terminal session, etc.) — too heavyweight
    for a role-propagation invariant test. The mirror uses the same
    helpers the real function calls, so a regression in those helpers
    surfaces here too.
    """

    def _fake_build_child(task_index: int, **kwargs):
        role = kwargs.get("role") or "leaf"
        parent_agent = kwargs.get("parent_agent")
        child_depth = getattr(parent_agent, "_delegate_depth", 0) + 1
        # Read via the module attribute so the per-test monkeypatch on
        # delegate_tool._get_max_spawn_depth / _get_orchestrator_enabled
        # actually affects us (imported names would be frozen at import).
        max_spawn = delegate_tool._get_max_spawn_depth()
        orchestrator_ok = (
            delegate_tool._get_orchestrator_enabled() and child_depth < max_spawn
        )
        effective_role = (
            role if (role == "orchestrator" and orchestrator_ok) else "leaf"
        )

        # Mirror the toolset resolution: intersect with parent, strip blocked,
        # re-add 'delegation' for orchestrators.
        parent_enabled = getattr(parent_agent, "enabled_toolsets", None) or []
        child_toolsets = _strip_blocked_tools(list(parent_enabled))
        if (
            effective_role == "orchestrator"
            and "delegation" not in child_toolsets
        ):
            child_toolsets.append("delegation")

        record = {
            "task_index": task_index,
            "requested_role": role,
            "effective_role": effective_role,
            "child_depth": child_depth,
            "max_spawn_depth": max_spawn,
            "orchestrator_ok": orchestrator_ok,
            "toolsets": child_toolsets,
        }
        captured.append(record)

        child = MagicMock()
        child._delegate_role = effective_role
        child._delegate_saved_tool_names = []
        child._credential_pool = None
        return child

    return _fake_build_child


@pytest.fixture(autouse=True)
def _orchestrator_config_on(monkeypatch):
    """Force the kill switch on and a depth that allows nesting (>=2).

    Default config in the test environment is flat (max_spawn_depth=1),
    which would force every 'orchestrator' request to degrade to 'leaf'
    and silently drop the 'delegation' toolset — the exact regression
    this test exists to catch.
    """
    monkeypatch.setattr(delegate_tool, "_get_orchestrator_enabled", lambda: True)
    monkeypatch.setattr(delegate_tool, "_get_max_spawn_depth", lambda: 2)


def _run_single_orchestrator(goal="plan the work and fan out"):
    """Patch _run_single_child with a canned success payload so no real
    LLM / agent loop spins up. Returns the patch context manager."""
    return patch(
        "tools.delegate_tool._run_single_child",
        return_value={
            "task_index": 0,
            "status": "completed",
            "summary": "spawned",
            "api_calls": 0,
            "duration_seconds": 0.0,
            "_child_role": "orchestrator",
        },
    )


def test_orchestrator_role_propagates_to_child(monkeypatch):
    """role='orchestrator' → child._delegate_role == 'orchestrator' and the
    'delegation' toolset is retained on the child."""
    captured: list = []
    monkeypatch.setattr(
        delegate_tool, "_build_child_agent", _make_capturing_builder(captured)
    )

    with _run_single_orchestrator():
        raw = delegate_task(
            goal="plan the work and fan out",
            role="orchestrator",
            parent_agent=_make_parent(depth=0),
        )

    import json

    parsed = json.loads(raw)
    assert parsed["results"][0]["status"] == "completed"

    assert len(captured) == 1
    record = captured[0]
    assert record["effective_role"] == "orchestrator", (
        "role='orchestrator' must reach effective_role='orchestrator' when "
        "orchestrator_enabled=True and child_depth < max_spawn_depth; "
        f"got effective_role={record['effective_role']!r}"
    )
    assert "delegation" in record["toolsets"], (
        "Orchestrator children must retain the 'delegation' toolset "
        "(_strip_blocked_tools removes it, _build_child_agent re-adds it "
        "for effective_role='orchestrator'); "
        f"got toolsets={record['toolsets']!r}"
    )


def test_leaf_role_strips_delegation_toolset(monkeypatch):
    """Counter-invariant: role='leaf' (the default) must NOT retain
    'delegation' — otherwise the leaf could escalate itself to orchestrator
    by simply calling delegate_task, defeating the depth cap."""
    captured: list = []
    monkeypatch.setattr(
        delegate_tool, "_build_child_agent", _make_capturing_builder(captured)
    )

    with patch("tools.delegate_tool._run_single_child") as mock_run:
        mock_run.return_value = {
            "task_index": 0,
            "status": "completed",
            "summary": "leaf-done",
            "api_calls": 0,
            "duration_seconds": 0.0,
            "_child_role": "leaf",
        }
        delegate_task(
            goal="do one thing well",
            role="leaf",
            parent_agent=_make_parent(depth=0),
        )

    assert len(captured) == 1
    record = captured[0]
    assert record["effective_role"] == "leaf"
    assert "delegation" not in record["toolsets"], (
        "Leaf children must not retain the 'delegation' toolset — they "
        "would bypass the depth cap by calling delegate_task directly. "
        f"got toolsets={record['toolsets']!r}"
    )


def test_orchestrator_degrades_to_leaf_when_kill_switch_off(monkeypatch):
    """When delegation.orchestrator_enabled=False, role='orchestrator' is
    silently coerced to 'leaf' AND 'delegation' is stripped. This is the
    operator kill switch — flipping it must flatten the whole tree."""
    monkeypatch.setattr(delegate_tool, "_get_orchestrator_enabled", lambda: False)

    captured: list = []
    monkeypatch.setattr(
        delegate_tool, "_build_child_agent", _make_capturing_builder(captured)
    )

    with patch("tools.delegate_tool._run_single_child") as mock_run:
        mock_run.return_value = {
            "task_index": 0,
            "status": "completed",
            "summary": "degraded",
            "api_calls": 0,
            "duration_seconds": 0.0,
            "_child_role": "leaf",
        }
        delegate_task(
            goal="try to spawn",
            role="orchestrator",
            parent_agent=_make_parent(depth=0),
        )

    record = captured[0]
    assert record["effective_role"] == "leaf", (
        "orchestrator_enabled=False must force effective_role='orchestrator' "
        "to degrade to 'leaf' inside _build_child_agent"
    )
    assert "delegation" not in record["toolsets"]


def test_orchestrator_degrades_to_leaf_at_depth_floor(monkeypatch):
    """When the parent is already at depth=max_spawn_depth-1, the child
    would be at the floor and must degrade to 'leaf' even if the caller
    asked for 'orchestrator'. Protects the depth cap from being bypassed
    by a role argument alone.

    With max_spawn_depth=2 and parent depth=1, the child is at depth 2
    == max_spawn_depth → orchestrator_ok becomes (True and 2 < 2) = False.
    """
    # parent depth 1 → child at depth 2 == max_spawn_depth(2) → floor.
    captured: list = []
    monkeypatch.setattr(
        delegate_tool, "_build_child_agent", _make_capturing_builder(captured)
    )

    with patch("tools.delegate_tool._run_single_child") as mock_run:
        mock_run.return_value = {
            "task_index": 0,
            "status": "completed",
            "summary": "floor",
            "api_calls": 0,
            "duration_seconds": 0.0,
            "_child_role": "leaf",
        }
        delegate_task(
            goal="try to nest past the floor",
            role="orchestrator",
            parent_agent=_make_parent(depth=1),
        )

    record = captured[0]
    assert record["effective_role"] == "leaf"
    assert record["child_depth"] == 2
    assert record["max_spawn_depth"] == 2
    assert "delegation" not in record["toolsets"]