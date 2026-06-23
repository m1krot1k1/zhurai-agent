"""Paths for the zhur.ai-agent ecosystem checkout (agents/, rules/, skills/).

Set ``ZHUR_AI_AGENT_ROOT`` to the repo root. When unset, falls back to the
Hermes install tree when ``<install>/agents`` exists (dev / fork layouts).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

_INSTALL_ROOT = Path(__file__).resolve().parent.parent


def get_ecosystem_root() -> Optional[Path]:
    """Return the ecosystem repo root, or None when not configured."""
    override = os.environ.get("ZHUR_AI_AGENT_ROOT", "").strip()

    if override:
        candidate = Path(os.path.expanduser(os.path.expandvars(override))).resolve()
        if candidate.is_dir():
            return candidate

    if (_INSTALL_ROOT / "agents").is_dir():
        return _INSTALL_ROOT.resolve()

    return None


def get_ecosystem_agents_dir() -> Optional[Path]:
    root = get_ecosystem_root()
    if root is None:
        return None
    agents = root / "agents"
    return agents if agents.is_dir() else None


def get_ecosystem_skills_dir() -> Optional[Path]:
    root = get_ecosystem_root()
    if root is None:
        return None
    skills = root / "skills"
    return skills if skills.is_dir() else None


def get_ecosystem_rules_dir() -> Optional[Path]:
    root = get_ecosystem_root()
    if root is None:
        return None
    rules = root / "rules"
    return rules if rules.is_dir() else None
