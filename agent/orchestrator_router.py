"""Runtime multi-agent routing for zhur.ai-agent ecosystem (Hermes delegate_task).

Heuristic gate + specialist scoring — mirrors the intent of Cursor's Task()
orchestration and Kanban auto-decompose, but for normal chat turns when the
ecosystem checkout is available (``ZHUR_AI_AGENT_ROOT`` or install ``agents/``).

Injected as API-call-time user-message context (never persisted) when
``delegation.auto_orchestrate`` is enabled.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

from agent.ecosystem_paths import get_ecosystem_root

logger = logging.getLogger(__name__)

# Keyword → ecosystem agent id (subset of skills/specialist-discovery/SKILL.md).
_SPECIALIST_KEYWORDS: dict[str, tuple[str, ...]] = {
    "repo-explorer": (
        "explore",
        "codebase",
        "structure",
        "navigate",
        "where is",
        "find file",
        "repository",
        "репозитор",
        "кодовой баз",
        "обход",
    ),
    "code": (
        "implement",
        "fix",
        "refactor",
        "write code",
        "add feature",
        "patch",
        "реализ",
        "исправ",
        "напиш",
        "добав",
    ),
    "code-reviewer": ("review", "code review", "ревью", "reviewer"),
    "test-specialist": ("test", "pytest", "coverage", "unit test", "тест"),
    "security-auditor": (
        "security",
        "vulnerability",
        "owasp",
        "cve",
        "audit",
        "безопас",
        "уязвим",
    ),
    "docs-specialist": ("document", "readme", "changelog", "docs", "документ"),
    "debug": ("debug", "bug", "error", "crash", "root cause", "отлад", "баг"),
    "frontend-specialist": (
        "react",
        "frontend",
        "ui",
        "component",
        "css",
        "typescript",
        "интерфейс",
    ),
    "devops-specialist": (
        "deploy",
        "ci/cd",
        "docker",
        "kubernetes",
        "pipeline",
        "infra",
        "деплой",
    ),
    "architect": ("architecture", "design", "adr", "архитект"),
}

# Default branch objectives when keyword scoring picks a specialist.
_AGENT_OBJECTIVES: dict[str, str] = {
    "repo-explorer": "Map the codebase: structure, key modules, and files relevant to the request",
    "code": "Implement or fix code per the user request; stay within assigned ownership",
    "code-reviewer": "Review code quality, patterns, and risks related to the user request",
    "test-specialist": "Identify test gaps and propose or add tests for the user request",
    "security-auditor": "Security review: attack surface, secrets, injection, OWASP concerns",
    "docs-specialist": "Document findings, gaps, and recommended changes for the user request",
    "debug": "Reproduce and diagnose bugs or failures described in the user request",
    "frontend-specialist": "Analyze or implement frontend/UI aspects of the user request",
    "devops-specialist": "Analyze CI/CD, deploy, and infra aspects of the user request",
    "architect": "Propose architecture and decomposition for the user request",
}

_VALID_ROUTER_AGENT_IDS = frozenset(_SPECIALIST_KEYWORDS) | frozenset(_AGENT_OBJECTIVES)

_ORCHESTRATOR_ROUTER_SYSTEM = """You decompose a user request into 2-5 parallel specialist branches.

Output a single JSON object only (no markdown fences):

{
  "fanout": true,
  "tasks": [
    {"agent_id": "repo-explorer", "objective": "<imperative, specific to this request>"},
    ...
  ]
}

Rules:
- Use 2-5 tasks. Prefer parallelism when branches are independent.
- agent_id MUST be one of: code, repo-explorer, code-reviewer, test-specialist,
  security-auditor, docs-specialist, debug, frontend-specialist, devops-specialist, architect
- Each objective is what a fresh worker reads with no other context.

If the request is genuinely single-focus (one specialist suffices), return:
{"fanout": false}
"""

_TRIVIAL_RE = re.compile(
    r"^\s*(?:"
    r"hi|hello|hey|thanks|thank you|ok|okay|yes|no|да|нет|привет|спасибо"
    r")\s*[!.?]*\s*$",
    re.IGNORECASE,
)

_ACTION_RE = re.compile(
    r"\b("
    r"implement|fix|analyze|analyse|refactor|review|migrate|add|create|build|"
    r"write|debug|deploy|test|explore|investigate|compare|audit|"
    r"реализ|исправ|анализ|рефактор|ревью|мигра|сделай|создай|напиш|исправь"
    r")\b",
    re.IGNORECASE,
)


def _load_delegation_cfg() -> dict:
    try:
        from hermes_cli.config import load_config

        return load_config().get("delegation") or {}
    except Exception:
        return {}


def orchestrate_mode() -> str:
    """Return ``hint``, ``programmatic``, or ``both``."""
    cfg = _load_delegation_cfg()
    mode = str(cfg.get("auto_orchestrate_mode", "programmatic")).strip().lower()
    if mode not in ("hint", "programmatic", "both"):
        return "programmatic"
    return mode


def is_llm_orchestrate_enabled() -> bool:
    cfg = _load_delegation_cfg()
    return bool(cfg.get("auto_orchestrate_llm", False))


def _min_parallel_tasks() -> int:
    cfg = _load_delegation_cfg()
    try:
        return max(2, int(cfg.get("auto_orchestrate_min_tasks", 2)))
    except (TypeError, ValueError):
        return 2


def is_auto_orchestrate_enabled() -> bool:
    if get_ecosystem_root() is None:
        return False
    cfg = _load_delegation_cfg()
    return bool(cfg.get("auto_orchestrate", True))


def _orchestration_scoring_text(message: str) -> str:
    """Text used for complexity/specialist scoring (strip bare slash commands)."""
    text = (message or "").strip()
    if not text:
        return ""
    if text.startswith("/"):
        # /start with a body is a full task, not a bare slash command.
        parts = text.split(maxsplit=1)
        if len(parts) > 1:
            return parts[1].strip()
        if "ORIGINAL_REQUEST:" in text:
            return extract_original_request(text) or text
        if "User task:" in text:
            return text.split("User task:", 1)[-1].strip()
        return ""
    return text


def extract_original_request(text: str) -> Optional[str]:
    """Pull ORIGINAL_REQUEST from delegate / router envelopes."""
    if not text or not isinstance(text, str):
        return None
    match = re.search(
        r"ORIGINAL_REQUEST:\s*(.+?)(?:\\n|\n(?:MODE:|ORCHESTRATOR_MUST:|AGENT_ID:)|$)",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if match:
        return " ".join(match.group(1).split())
    return None


def infer_agent_id_from_text(text: str) -> Optional[str]:
    """Best-effort agent id when delegate context omits AGENT_ID."""
    explicit = parse_agent_id_from_envelope(text or "")
    if explicit:
        return explicit
    scored = score_specialists(text or "")
    if not scored:
        return None
    best_id, best_score = scored[0]
    if best_score < 1:
        return None
    # Require a clear winner so ambiguous goals do not get random labels.
    if len(scored) > 1 and scored[1][1] >= best_score:
        return None
    return best_id


def enrich_delegate_task_entry(task: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure each batch entry carries AGENT_ID in context when inferrable."""
    from agent.ecosystem_delegate import build_delegate_branch_context

    goal = str(task.get("goal") or "").strip()
    context = str(task.get("context") or "").strip()
    agent_id = parse_agent_id_from_envelope(context) or parse_agent_id_from_envelope(goal)
    if not agent_id:
        agent_id = infer_agent_id_from_text(f"{goal}\n{context}")
    if not agent_id:
        return task
    if parse_agent_id_from_envelope(context):
        return task
    original = extract_original_request(context) or extract_original_request(goal) or ""
    objective = goal or _objective_for_agent(agent_id, original or context)
    enriched = dict(task)
    enriched["context"] = build_delegate_branch_context(
        agent_id,
        objective=objective,
        original_request=original,
    )
    return enriched


def classify_complexity(message: str) -> str:
    """Return ``trivial``, ``single``, or ``multi``."""
    text = _orchestration_scoring_text(message)
    if not text:
        raw = (message or "").strip()
        if not raw or (raw.startswith("/") and len(raw.split(maxsplit=1)) == 1):
            return "trivial"
        text = raw
    if len(text) < 35 and _TRIVIAL_RE.match(text):
        return "trivial"
    if len(text) < 25 and "?" in text and not _ACTION_RE.search(text):
        return "trivial"

    action_hits = len(_ACTION_RE.findall(text))
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    multi_signal = (
        len(text) >= 120
        or action_hits >= 2
        or len(lines) >= 4
        or text.count("\n- ") >= 2
        or text.count(". ") >= 3
    )
    if multi_signal:
        return "multi"
    if action_hits >= 1 or len(text) >= 80:
        return "single"
    return "trivial"


def score_specialists(message: str) -> List[Tuple[str, float]]:
    """Score ecosystem agents against *message*; higher is better."""
    text = (message or "").lower()
    if not text:
        return []

    scores: List[Tuple[str, float]] = []
    for agent_id, keywords in _SPECIALIST_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text)
        if hits:
            scores.append((agent_id, float(hits)))
    scores.sort(key=lambda pair: pair[1], reverse=True)
    return scores


def suggest_specialists(message: str, *, max_branches: int = 4) -> List[str]:
    """Return ordered agent ids for a first parallel wave."""
    scored = score_specialists(message)
    if scored:
        ids = [agent_id for agent_id, _ in scored[:max_branches]]
    else:
        ids = ["repo-explorer", "code-reviewer"]

    # Repo analysis / full-stack tasks benefit from a security pass.
    if "security-auditor" not in ids and classify_complexity(message) == "multi":
        if len(ids) < max_branches:
            ids.append("security-auditor")
        elif "code-reviewer" in ids:
            ids[-1] = "security-auditor"

    # Dedupe while preserving order.
    seen: set[str] = set()
    out: List[str] = []
    for agent_id in ids:
        if agent_id not in seen:
            seen.add(agent_id)
            out.append(agent_id)
    return out[:max_branches]


def should_programmatic_orchestrate(message: str) -> bool:
    if not is_auto_orchestrate_enabled():
        return False
    if orchestrate_mode() not in ("programmatic", "both"):
        return False
    return classify_complexity(message) == "multi"


def is_start_router_turn(message: str) -> bool:
    """True for ``/start`` and router-mode skill injections."""
    text = (message or "").strip()
    if not text:
        return False
    if text.startswith("/start"):
        return True
    lower = text.lower()
    return "router mode" in lower and "/start" in lower


def _agent_ecosystem_id(agent) -> Optional[str]:
    ctx = getattr(agent, "_delegate_branch_context", "") or ""
    return parse_agent_id_from_envelope(ctx)


def _resolve_original_request(agent, user_message: str) -> str:
    """Best-effort ORIGINAL_REQUEST from envelope + turn message."""
    original = ""
    for src in (
        user_message or "",
        getattr(agent, "_delegate_branch_context", "") or "",
        getattr(agent, "ephemeral_system_prompt", "") or "",
    ):
        if not isinstance(src, str) or not src.strip():
            continue
        original = extract_original_request(src) or original
    if original:
        return original
    if "User task:" in (user_message or ""):
        return user_message.split("User task:", 1)[-1].strip()
    return _orchestration_scoring_text(user_message) or (user_message or "").strip()


def should_auto_orchestrate(message: str) -> bool:
    if not is_auto_orchestrate_enabled():
        return False
    if orchestrate_mode() == "programmatic":
        return False
    return classify_complexity(message) == "multi"


def _objective_for_agent(agent_id: str, message: str) -> str:
    base = _AGENT_OBJECTIVES.get(agent_id, f"Execute the user request as {agent_id}")
    snippet = " ".join((message or "").split())
    if len(snippet) > 120:
        snippet = snippet[:117] + "..."
    return f"{base}. User request: {snippet}"


def _tasks_from_agent_specs(
    specs: Sequence[Tuple[str, str]],
    original_request: str,
) -> List[Dict[str, Any]]:
    from agent.ecosystem_delegate import build_delegate_branch_context

    tasks: List[Dict[str, Any]] = []
    for agent_id, objective in specs:
        ctx = build_delegate_branch_context(
            agent_id,
            objective=objective,
            original_request=original_request,
        )
        tasks.append(
            {
                "goal": objective,
                "context": ctx,
                "role": "leaf",
            }
        )
    return tasks


def plan_parallel_delegate_tasks(message: str) -> List[Dict[str, Any]]:
    """Build delegate_task batch entries for a parallel first wave."""
    text = _orchestration_scoring_text(message) or (message or "").strip()
    if not text:
        return []

    llm_specs = _plan_tasks_with_llm(text) if is_llm_orchestrate_enabled() else None
    if llm_specs:
        specs = llm_specs
    else:
        agent_ids = suggest_specialists(text)
        min_tasks = _min_parallel_tasks()
        if len(agent_ids) < min_tasks:
            for fallback in ("repo-explorer", "code-reviewer", "security-auditor"):
                if fallback not in agent_ids:
                    agent_ids.append(fallback)
                if len(agent_ids) >= min_tasks:
                    break
        specs = [(aid, _objective_for_agent(aid, text)) for aid in agent_ids[:5]]

    return _tasks_from_agent_specs(specs, text)


def _extract_json_blob(raw: str) -> Optional[dict]:
    text = (raw or "").strip()
    if not text:
        return None
    if text.startswith("{"):
        try:
            parsed = json.loads(text)
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            pass
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def _plan_tasks_with_llm(message: str) -> Optional[List[Tuple[str, str]]]:
    """Optional auxiliary LLM decomposition; returns None on any failure."""
    try:
        from agent.auxiliary_client import get_auxiliary_extra_body, get_text_auxiliary_client
    except Exception as exc:
        logger.debug("orchestrator_router: auxiliary import failed: %s", exc)
        return None

    try:
        client, model = get_text_auxiliary_client("orchestrator_router")
    except Exception as exc:
        logger.debug("orchestrator_router: aux client unavailable: %s", exc)
        return None
    if client is None or not model:
        return None

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _ORCHESTRATOR_ROUTER_SYSTEM},
                {"role": "user", "content": message},
            ],
            temperature=0.2,
            max_tokens=2000,
            timeout=120,
            extra_body=get_auxiliary_extra_body() or None,
        )
        raw = resp.choices[0].message.content or ""
    except Exception as exc:
        logger.info("orchestrator_router LLM failed: %s", exc)
        return None

    parsed = _extract_json_blob(raw)
    if not parsed or not parsed.get("fanout"):
        return None

    raw_tasks = parsed.get("tasks")
    if not isinstance(raw_tasks, list) or len(raw_tasks) < 2:
        return None

    specs: List[Tuple[str, str]] = []
    for entry in raw_tasks:
        if not isinstance(entry, dict):
            continue
        agent_id = str(entry.get("agent_id") or "").strip()
        objective = str(entry.get("objective") or "").strip()
        if agent_id not in _VALID_ROUTER_AGENT_IDS or not objective:
            continue
        specs.append((agent_id, objective))

    return specs if len(specs) >= 2 else None


def format_programmatic_dispatch_message(
    tasks: Sequence[Dict[str, Any]],
    dispatch_payload: dict,
) -> str:
    labels: List[str] = []
    for task in tasks:
        ctx = str(task.get("context") or "")
        agent_id = parse_agent_id_from_envelope(ctx) or str(task.get("goal") or "specialist")
        labels.append(agent_id)

    label_csv = ", ".join(labels)
    status = dispatch_payload.get("status")
    if status == "dispatched":
        count = dispatch_payload.get("count") or len(tasks)
        return (
            f"Запущено {count} параллельных специалистов ({label_csv}). "
            "Они работают в фоне — результаты появятся по мере завершения."
        )

    results = dispatch_payload.get("results")
    if isinstance(results, list) and results:
        return (
            f"Выполнено {len(results)} делегированных веток ({label_csv}). "
            "Сводка в tool result."
        )

    note = dispatch_payload.get("note") or dispatch_payload.get("error") or ""
    if note:
        return f"Оркестрация: {label_csv}. {note}"
    return f"Оркестрация запущена: {label_csv}."


def format_start_router_dispatch_message(dispatch_payload: dict) -> str:
    status = dispatch_payload.get("status")
    if status == "dispatched":
        return (
            "Запущен сабагент **start** → он передаст задачу **orchestrator** → "
            "затем orchestrator запустит параллельных специалистов. "
            "Следите за Spawn tree."
        )
    note = dispatch_payload.get("note") or dispatch_payload.get("error") or ""
    if note:
        return f"Start router: {note}"
    return "Start router: делегирование orchestrator."


def format_start_handoff_message(dispatch_payload: dict) -> str:
    status = dispatch_payload.get("status")
    if status == "dispatched":
        return (
            "Start → **orchestrator**: координатор запущен, "
            "готовлю параллельный рой специалистов."
        )
    note = dispatch_payload.get("note") or dispatch_payload.get("error") or ""
    if note:
        return f"Start handoff: {note}"
    return "Start передал задачу orchestrator."


def try_programmatic_start_router(
    agent, message: str, *, task_id: str
) -> Optional[str]:
    """Root ``/start``: spawn start subagent (not leaf specialists)."""
    from agent.ecosystem_delegate import build_delegate_branch_context

    original = _resolve_original_request(agent, message)
    if not original:
        return None

    logger.info(
        "start router: dispatching start subagent (session=%s task=%s)",
        getattr(agent, "session_id", None) or "none",
        task_id,
    )

    ctx = build_delegate_branch_context(
        "start",
        objective="Route ORIGINAL_REQUEST to orchestrator (FIRST_ACTION gate)",
        original_request=original,
        extra={"MODE": "start_router"},
    )

    try:
        result_json = agent._dispatch_delegate_task(
            {
                "goal": "Start router: hand off to orchestrator",
                "context": ctx,
                "role": "orchestrator",
                "background": True,
            }
        )
    except Exception as exc:
        logger.warning("start router dispatch failed: %s", exc)
        return None

    try:
        payload = json.loads(result_json)
    except json.JSONDecodeError:
        return None

    if payload.get("error"):
        logger.info("start router rejected: %s", payload.get("error"))
        return None

    return format_start_router_dispatch_message(payload)


def try_start_child_handoff(
    agent, user_message: str, *, task_id: str
) -> Optional[str]:
    """Start subagent → orchestrator before the start LLM turn."""
    if _agent_ecosystem_id(agent) != "start":
        return None
    if getattr(agent, "_start_handoff_done", False):
        return None

    valid = getattr(agent, "valid_tool_names", None) or set()
    if "delegate_task" not in valid:
        return None

    try:
        from tools.delegate_tool import is_spawn_paused

        if is_spawn_paused():
            return None
    except Exception:
        pass

    original = _resolve_original_request(agent, user_message)
    if not original:
        return None

    from agent.ecosystem_delegate import build_delegate_branch_context

    ctx = build_delegate_branch_context(
        "orchestrator",
        objective="Coordinate user request and delegate parallel specialist branches",
        original_request=original,
        extra={
            "MODE": "multi_domain",
            "ORCHESTRATOR_MUST": (
                "decompose into 2+ independent branches; first wave MUST use "
                "delegate_task(tasks=[...]) with parallel specialists"
            ),
        },
    )

    logger.info(
        "start handoff: dispatching orchestrator (session=%s task=%s)",
        getattr(agent, "session_id", None) or "none",
        task_id,
    )

    try:
        result_json = agent._dispatch_delegate_task(
            {
                "goal": "Coordinate user request",
                "context": ctx,
                "role": "orchestrator",
                "background": True,
            }
        )
    except Exception as exc:
        logger.warning("start handoff failed: %s", exc)
        return None

    try:
        payload = json.loads(result_json)
    except json.JSONDecodeError:
        return None

    if payload.get("error"):
        logger.info("start handoff rejected: %s", payload.get("error"))
        return None

    agent._start_handoff_done = True
    return format_start_handoff_message(payload)


def try_programmatic_orchestration(agent, message: str, *, task_id: str) -> Optional[str]:
    """Programmatically fan out delegate_task before the root LLM turn.

    Returns an assistant-facing message when dispatch succeeded, else None
    (caller falls back to hint injection + normal LLM loop).
    """
    if not should_programmatic_orchestrate(message):
        return None
    if getattr(agent, "_delegate_depth", 0) > 0:
        return None

    valid = getattr(agent, "valid_tool_names", None) or set()
    if "delegate_task" not in valid:
        logger.debug("programmatic orchestration skipped: delegate_task unavailable")
        return None

    try:
        from tools.delegate_tool import is_spawn_paused

        if is_spawn_paused():
            logger.info("programmatic orchestration skipped: spawn paused")
            return None
    except Exception:
        pass

    if is_start_router_turn(message):
        return try_programmatic_start_router(agent, message, task_id=task_id)

    tasks = plan_parallel_delegate_tasks(message)
    if len(tasks) < _min_parallel_tasks():
        return None

    logger.info(
        "programmatic orchestration: dispatching %d parallel tasks (session=%s task=%s)",
        len(tasks),
        getattr(agent, "session_id", None) or "none",
        task_id,
    )

    try:
        result_json = agent._dispatch_delegate_task({"tasks": tasks, "role": "leaf"})
    except Exception as exc:
        logger.warning("programmatic orchestration dispatch failed: %s", exc)
        return None

    try:
        payload = json.loads(result_json)
    except json.JSONDecodeError:
        logger.warning("programmatic orchestration: non-JSON delegate result")
        return None

    if payload.get("error"):
        logger.info("programmatic orchestration rejected: %s", payload.get("error"))
        return None

    return format_programmatic_dispatch_message(tasks, payload)


def try_orchestrator_child_fanout(agent, user_message: str, *, task_id: str) -> Optional[str]:
    """Parallel first wave when the active agent is an orchestrator subagent.

    Root ``/start`` often spawns a single orchestrator child; without this hook
    the model tends to call ``delegate_task`` once per specialist (sequential).
    """
    if getattr(agent, "_delegate_role", None) != "orchestrator":
        return None
    if _agent_ecosystem_id(agent) == "start":
        return None
    if getattr(agent, "_orchestrator_fanout_done", False):
        return None

    valid = getattr(agent, "valid_tool_names", None) or set()
    if "delegate_task" not in valid:
        return None

    try:
        from tools.delegate_tool import is_spawn_paused

        if is_spawn_paused():
            return None
    except Exception:
        pass

    original = _resolve_original_request(agent, user_message)
    if not original:
        return None

    tasks = plan_parallel_delegate_tasks(original)
    if len(tasks) < _min_parallel_tasks():
        return None

    tasks = [enrich_delegate_task_entry(t) for t in tasks]
    logger.info(
        "orchestrator child fan-out: dispatching %d parallel tasks (session=%s task=%s)",
        len(tasks),
        getattr(agent, "session_id", None) or "none",
        task_id,
    )

    try:
        result_json = agent._dispatch_delegate_task(
            {"tasks": tasks, "role": "leaf", "background": True}
        )
    except Exception as exc:
        logger.warning("orchestrator child fan-out failed: %s", exc)
        return None

    try:
        payload = json.loads(result_json)
    except json.JSONDecodeError:
        return None

    if payload.get("error"):
        logger.info("orchestrator child fan-out rejected: %s", payload.get("error"))
        return None

    agent._orchestrator_fanout_done = True
    return format_programmatic_dispatch_message(tasks, payload)


def build_orchestration_injection(message: str) -> Optional[str]:
    """Build API-only user-message injection for multi-domain turns."""
    if not should_auto_orchestrate(message):
        return None

    specialists = suggest_specialists(message)
    specialist_csv = ", ".join(specialists)
    # Keep ORIGINAL_REQUEST on one line for downstream parsers.
    original = " ".join((message or "").split())

    return (
        "[HERMES_MULTI_AGENT_ROUTER — orchestration hint; not shown to user]\n"
        "This turn requires multi-agent orchestration. Your FIRST action MUST be "
        'ONE delegate_task call with role="orchestrator" (no text reply, no '
        "read_file/terminal/web before it).\n\n"
        "Required first call shape:\n"
        'delegate_task(role="orchestrator", '
        'goal="Coordinate user request", '
        f'context="ORIGINAL_REQUEST: {original}\\n'
        "MODE: multi_domain\\n"
        "ORCHESTRATOR_MUST: decompose into 2+ independent parallel branches via "
        "delegate_task(tasks=[...]); first wave specialists (use build_delegate "
        f"branch context with AGENT_ID): {specialist_csv}; NEVER assign one leaf "
        'for the entire analysis; orchestrator delegates only — does not implement.")\n\n'
        "Each tasks[] entry must set context with AGENT_ID + AGENT_BRIEF_PATH "
        "(read brief at branch start). Simple greetings only: answer directly."
    )


def parse_agent_id_from_envelope(text: str) -> Optional[str]:
    """Extract ecosystem agent id from delegate_task / Task() envelope."""
    if not text:
        return None
    for pattern in (
        r"^AGENT_ID:\s*(\S+)",
        r"\bAGENT_ID:\s*(\S+)",
        r"AGENT_BRIEF_PATH:\s*.*?/agents/([\w-]+)\.md",
        r'subagent_type\s*[=:]\s*["\']?([\w-]+)',
        r'Task\s*\(\s*subagent_type\s*=\s*["\']([\w-]+)["\']',
    ):
        match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
        if match:
            candidate = match.group(1).strip().lower()
            if candidate in _VALID_ROUTER_AGENT_IDS or candidate in ("orchestrator", "start"):
                return candidate
    return None
