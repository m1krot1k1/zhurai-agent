"""Agent brief parity between runtime agents/ and references/agents/."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME = REPO_ROOT / "agents"
REFERENCES = (
    REPO_ROOT / "skills" / "multi-agent-ecosystem" / "references" / "agents"
)


def _agent_ids(directory: Path) -> set[str]:
    return {p.stem for p in directory.glob("*.md") if p.name != "README.md"}


@pytest.mark.parametrize(
    "tree",
    [RUNTIME, REFERENCES],
    ids=["runtime", "references"],
)
def test_thirty_three_agents_present(tree: Path) -> None:
    assert len(_agent_ids(tree)) == 33


def test_runtime_matches_references_agent_ids() -> None:
    assert _agent_ids(RUNTIME) == _agent_ids(REFERENCES)
