"""Build delegate_task envelopes from zhur.ai-agent ecosystem agent briefs."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from agent.ecosystem_paths import get_ecosystem_root


def resolve_agent_brief(agent_id: str) -> Optional[Path]:
    """Return the first existing brief path for *agent_id* under the ecosystem root."""
    root = get_ecosystem_root()
    if root is None:
        return None

    slug = agent_id.strip().lower().replace("_", "-")
    candidates = (
        root / "agents" / f"{slug}.md",
        root
        / "skills"
        / "multi-agent-ecosystem"
        / "references"
        / "agents"
        / f"{slug}.md",
    )
    for path in candidates:
        if path.is_file():
            return path.resolve()
    return None


def build_delegate_branch_context(
    agent_id: str,
    *,
    objective: str,
    original_request: str = "",
    ownership: str = "",
    extra: Optional[Dict[str, Any]] = None,
) -> str:
    """Compose a branch *context* string for delegate_task (child reads brief from path)."""
    brief = resolve_agent_brief(agent_id)
    lines = [
        f"OBJECTIVE: {objective.strip()}",
        f"AGENT_ID: {agent_id.strip()}",
    ]
    if original_request.strip():
        lines.append(f"ORIGINAL_REQUEST: {original_request.strip()}")
    if ownership.strip():
        lines.append(f"OWNERSHIP: {ownership.strip()}")
    if brief is not None:
        lines.append(f"AGENT_BRIEF_PATH: {brief}")
        lines.append(
            "NON-NEGOTIABLE: Read AGENT_BRIEF_PATH at the start of the branch "
            "and operate strictly in that role."
        )
    for key, value in (extra or {}).items():
        if value is not None and str(value).strip():
            lines.append(f"{key.upper()}: {value}")
    return "\n".join(lines)


def list_ecosystem_agent_ids() -> list[str]:
    """List agent ids discovered under agents/ (runtime tree)."""
    root = get_ecosystem_root()
    if root is None:
        return []
    agents_dir = root / "agents"
    if not agents_dir.is_dir():
        return []
    return sorted(
        p.stem
        for p in agents_dir.glob("*.md")
        if p.name != "README.md"
    )
