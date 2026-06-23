#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CASE_FILE = ROOT / "benchmarks" / "transcript-cases.json"
COORDINATION_AGENTS = {"start", "orchestrator", "meta-agent-architect", "subagent-factory"}
NON_WRITER_AGENTS = {
    "agent-architect",
    "architect",
    "ask",
    "bug-triage",
    "code-reviewer",
    "code-skeptic",
    "meta-agent-architect",
    "orchestrator",
    "review",
    "security-auditor",
    "start",
}
CANONICAL_LABELS = [
    "OBJECTIVE",
    "SCOPE",
    "OUT_OF_SCOPE",
    "OWNERSHIP",
    "DEPENDENCIES",
    "STEPS",
    "DELIVERABLES",
    "ACCEPTANCE_CRITERIA",
    "NON-NEGOTIABLE",
    "COMPLETION_CONTRACT",
]
TASK_RE = re.compile(r'Task\s*\(\s*subagent_type\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
ORCHESTRATOR_TASK_RE = re.compile(
    r'Task\s*\(\s*subagent_type\s*=\s*["\']orchestrator["\']',
    re.IGNORECASE,
)
START_CMD_RE = re.compile(r"(?<![\w/])\/start\b", re.IGNORECASE)
START_LOCAL_WORK_RE = re.compile(
    r"\b(read|reading|run|running|list|listing|compare|diff|scan|scanning|explore|exploring|grep|rg|cat|ls|git)\b|"
    r"\b(читаем|прочитать|запускаем|запустить|смотрим|сравниваем|ищем|поиск|листинг|проверим|валидатор|дифф)\b",
    re.IGNORECASE,
)
TASK_UNAVAILABLE_RE = re.compile(
    r"no Task tool|Task tool unavailable|Task unavailable|MULTI_AGENT_PIPELINE_BLOCKED",
    re.IGNORECASE,
)
SINGLE_AGENT_DEGRADED_RE = re.compile(r"SINGLE_AGENT_DEGRADED_MODE", re.IGNORECASE)
FAKE_ORCH_AFTER_UNAVAILABLE_RE = re.compile(
    r"executing the orchestration plan ourselves|running validators|fixing |edited |parallel|branches|orchestrat",
    re.IGNORECASE,
)
RELAY_MARKER_RE = re.compile(
    r"relay_required|pause_reason\s*:\s*RELAY_REQUIRED|root_task_proxy|proxy_orchestrator_packet|resume_packet",
    re.IGNORECASE,
)
ORCHESTRATOR_RELAY_REQUEST_RE = re.compile(
    r"ORCHESTRATOR_RELAY_REQUEST|relay_batch_id|resume_orchestrator_packet",
    re.IGNORECASE,
)
ORCHESTRATOR_CHILD_PROXY_RE = re.compile(
    r"RELAY_MODE:\s*(?:orchestrator_child_proxy|parent_task_proxy)|RELAY_SOURCE:\s*orchestrator",
    re.IGNORECASE,
)
ORCHESTRATOR_RELAY_RESUME_RE = re.compile(
    r"RELAY_MODE:\s*child_results_return|ENTRY_MODE:\s*relay_resume",
    re.IGNORECASE,
)
ORCHESTRATOR_SELF_RECURSION_RE = re.compile(
    r"another root routing|open another root|plan everything from scratch",
    re.IGNORECASE,
)
CONTINUOUS_ORCHESTRATOR_FOLLOWUP_RE = re.compile(
    r"CONTINUATION_PACKET\s*:|WAVE_NUMBER\s*:\s*(?:[2-9]|\d{2,})\b",
    re.IGNORECASE,
)
COMPLETION_CLAIM_RE = re.compile(
    r"\b(done|completed|finished|выполнено|готово|завершено)\b",
    re.IGNORECASE,
)
EVIDENCE_TOKEN_RE = re.compile(
    r"(?:[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+\.[A-Za-z0-9_-]+)|"
    r"(?:\b(?:exit\s*0|python3\s+[A-Za-z0-9_./-]+|git\s+status|tests?\s+passed|benchmark[s]?\s+passed)\b)",
    re.IGNORECASE,
)
OPEN_ENDED_IMPROVEMENT_RE = re.compile(
    r"самоулучш|self-improv|continuous improvement|вектор(?:ы)? улучшени|улучшай|улучшен|improv(?:e|ing|ement)|keep improving|continue improving|во все стороны",
    re.IGNORECASE,
)
UNTIL_STOP_RE = re.compile(
    r"24/7|CONTINUOUS_MODE\s*:\s*until_user_stop|until_user_stop|until i say stop|until user stop|keep working|continue working|пока не .*стоп|продолжай работать",
    re.IGNORECASE,
)
SWARM_OR_START_RE = re.compile(
    r"(?<![\w/])\/start\b|swarm|рой|ENTRY_MODE\s*:\s*start_worker_wave|ROOT_START_PROFILE\s*:\s*FULL_FORCE_START_PROFILE",
    re.IGNORECASE,
)
STATUS_DONE_RE = re.compile(r"status\s*:\s*(?:done|approval)\b", re.IGNORECASE)
RECOMMENDED_STOP_RE = re.compile(r"recommended_action\s*:\s*stop\b", re.IGNORECASE)
STATUS_CONTINUE_RE = re.compile(r"status\s*:\s*(?:continue|pause|relay_required)\b", re.IGNORECASE)
NEXT_PACKET_NONE_RE = re.compile(
    r"(?:next_packet|resume_packet)\s*:\s*(?:none|null|n/?a|tbd|empty|''|\"\"|-)\b",
    re.IGNORECASE,
)
STEADY_STATE_PROOF_RE = re.compile(
    r"status\s*:\s*steady_state\b|steady_state_evidence|remaining_vectors\s*:\s*0\b|no meaningful backlog remains|нет оставшихся осмысленных векторов|бэклог исчерпан|backlog exhausted",
    re.IGNORECASE,
)
PAUSE_OR_BLOCK_RE = re.compile(
    r"PAUSED_FOR_RUNTIME_BUDGET|status\s*:\s*(?:paused|pause|blocked|relay_required|continue)\b|MULTI_AGENT_PIPELINE_BLOCKED",
    re.IGNORECASE,
)
START_RESUME_TASK_RE = re.compile(
    r'Task\s*\(\s*subagent_type\s*=\s*["\']start["\'][^)]*?\bresume\s*=',
    re.IGNORECASE | re.DOTALL,
)
TURN_BOUNDARY_CONTINUE_RE = re.compile(
    r"status\s*:\s*(?:continue|pause|relay_required)\b[\s\S]*?(?:PAUSED_FOR_RUNTIME_BUDGET|runtime_boundary\s*:\s*turn[_ -]?boundary)",
    re.IGNORECASE,
)
WATCHDOG_BACKOFF_RE = re.compile(
    r"retry_backoff|backoff_seconds|retry_attempt|heartbeat_interval",
    re.IGNORECASE,
)
NO_PROGRESS_GUARD_RE = re.compile(
    r"no_progress|stalled_waves|no_progress_waves|stall_limit",
    re.IGNORECASE,
)
BLOCKER_TAXONOMY_RE = re.compile(
    r"BLOCKED_(?:RUNTIME|POLICY|INPUT|EXTERNAL|INTEGRATION)",
    re.IGNORECASE,
)
LEGACY_RUNTIME_STATUS_RE = re.compile(
    r"status\s*:\s*(done|continue|relay_required)\b",
    re.IGNORECASE,
)
STATUS_RESUME_RE = re.compile(r"status\s*:\s*resume\b", re.IGNORECASE)
PAUSE_STATE_RE = re.compile(
    r"status\s*:\s*pause\b|execution_state\s*:\s*paused\b|approval_state\s*:\s*requested\b|pause_reason\s*:",
    re.IGNORECASE,
)
EXPLICIT_RESUME_EVENT_RE = re.compile(
    r"resume_event\s*:\s*(?:approval_granted|input_received|dependency_resolved)|approval_granted|input_received|dependency_resolved",
    re.IGNORECASE,
)
RELAY_RESUME_TASK_RE = re.compile(
    r"ENTRY_MODE\s*:\s*relay_resume|\bresume\s*=",
    re.IGNORECASE,
)


@dataclass
class Message:
    index: int
    speaker: str | None
    text: str


@dataclass
class Delegate:
    subagent: str
    prompt: str
    message_index: int
    speaker: str | None


@dataclass
class Finding:
    code: str
    severity: str
    message: str
    message_index: int | None = None


@dataclass
class Report:
    path: Path
    status: str
    messages: list[Message]
    delegates: list[Delegate]
    findings: list[Finding]


def load_json(path: Path) -> Any:
    last_error: Exception | None = None
    for encoding in ("utf-8", "utf-8-sig"):
        try:
            return json.loads(path.read_text(encoding=encoding))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            last_error = exc
    raise RuntimeError(f"Could not parse JSON from {path}: {last_error}")


def flatten_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(flatten_text(item) for item in value)
    if isinstance(value, dict):
        for key in ("text", "message", "content", "body", "prompt", "quote"):
            if key in value:
                return flatten_text(value[key])
        return ""
    return str(value)


def best_speaker(item: dict[str, Any]) -> str | None:
    for key in ("speaker", "from", "actor", "author", "role", "name", "agent"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def synthesize_delegate_text(item: dict[str, Any]) -> str:
    subagent = flatten_text(
        item.get("subagent") or item.get("subagent_type") or item.get("agent")
    ).strip()
    prompt = flatten_text(item.get("prompt") or item.get("text") or item.get("content"))
    if not subagent:
        return prompt
    return f'Task(subagent_type="{subagent}", prompt="""{prompt}""")'


def extract_messages(data: Any) -> list[Message]:
    if isinstance(data, dict):
        if isinstance(data.get("messages"), list):
            raw_items = data["messages"]
        elif isinstance(data.get("events"), list):
            raw_items = data["events"]
        else:
            raw_items = [data]
    elif isinstance(data, list):
        raw_items = data
    else:
        raw_items = [data]

    messages: list[Message] = []
    for index, item in enumerate(raw_items):
        if isinstance(item, str):
            text = item
            speaker = None
        elif isinstance(item, dict):
            speaker = best_speaker(item)
            if item.get("type") == "delegate" or item.get("subagent") or item.get("subagent_type"):
                text = synthesize_delegate_text(item)
            else:
                text = flatten_text(
                    item.get("text")
                    or item.get("message")
                    or item.get("content")
                    or item.get("body")
                    or item.get("prompt")
                    or item.get("quote")
                )
        else:
            speaker = None
            text = str(item)

        if text.strip():
            messages.append(Message(index=index, speaker=speaker, text=text))
    return messages


def extract_delegates(messages: list[Message]) -> list[Delegate]:
    delegates: list[Delegate] = []
    for message in messages:
        matches = list(TASK_RE.finditer(message.text))
        for idx, match in enumerate(matches):
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(message.text)
            prompt = message.text[match.start() : end].strip()
            delegates.append(
                Delegate(
                    subagent=match.group(1).strip(),
                    prompt=prompt,
                    message_index=message.index,
                    speaker=message.speaker,
                )
            )
    return delegates


def normalize_speaker(value: str | None) -> str | None:
    if not value:
        return None
    return value.strip().lower()


def relative_label(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def error(
    findings: dict[tuple[str, int | None], Finding],
    code: str,
    message: str,
    message_index: int | None = None,
) -> None:
    findings[(code, message_index)] = Finding(
        code=code,
        severity="error",
        message=message,
        message_index=message_index,
    )


def is_writer_agent(name: str) -> bool:
    normalized = name.strip()
    if not normalized:
        return False
    if normalized in COORDINATION_AGENTS:
        return False
    if normalized in NON_WRITER_AGENTS:
        return False
    return True


def is_supervised_worker_start(prompt: str) -> bool:
    lowered = prompt.lower()
    return (
        "entry_mode: supervised_worker" in lowered
        or "supervised_worker" in lowered
        or "worker-start" in lowered
    )


def orchestrator_prompt_has_original_request(prompt: str) -> bool:
    return "original_request:" in prompt.lower()


def is_analyzer_start(prompt: str) -> bool:
    lowered = prompt.lower()
    return (
        "entry_mode: analyzer_only" in lowered
        or "analyzer role only" in lowered
        or "analyzer only" in lowered
        or "analyzer" in lowered
        or "analyze" in lowered
        or "verdict" in lowered
        or "done or continue" in lowered
        or "готово / не готово" in lowered
        or "approval | blocked | pause | resume" in lowered
        or "approval/blocked/pause/resume" in lowered
    )


def has_prior_orchestrator_relay_request(messages: list[Message], index: int) -> bool:
    return any(
        message.index < index and ORCHESTRATOR_RELAY_REQUEST_RE.search(message.text)
        for message in messages
    )


def extract_labeled_section(text: str, label: str) -> str:
    next_labels = "|".join(re.escape(item) for item in CANONICAL_LABELS if item != label)
    pattern = re.compile(
        rf"{re.escape(label)}\s*:\s*(.*?)(?=(?:{next_labels})\s*:|$)",
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def ownership_tokens(section: str) -> list[str]:
    tokens = re.findall(
        r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.*{}-]+)+/?|[A-Za-z0-9_.-]+\.[A-Za-z0-9_*.-]+",
        section,
    )
    normalized: list[str] = []
    for token in tokens:
        cleaned = token.strip("`'\"()[]{}.,;:").replace("\\", "/")
        if not cleaned:
            continue
        if "/" not in cleaned and "." not in cleaned and "*" not in cleaned:
            continue
        normalized.append(cleaned.lstrip("./"))
    return normalized


def ownership_anchors(tokens: list[str]) -> list[str]:
    anchors: list[str] = []
    for token in tokens:
        first_glob = min(
            [idx for idx in (token.find("*"), token.find("{"), token.find("[")) if idx != -1],
            default=-1,
        )
        if first_glob != -1:
            prefix = token[:first_glob]
            if "/" in prefix:
                prefix = prefix.rsplit("/", 1)[0] + "/"
            else:
                prefix = prefix + "/"
            anchors.append(prefix)
            continue
        anchors.append(token)
    return anchors


def ownership_sets_overlap(left: list[str], right: list[str]) -> bool:
    for a in ownership_anchors(left):
        for b in ownership_anchors(right):
            if a == b:
                return True
            if a.endswith("/") and b.startswith(a):
                return True
            if b.endswith("/") and a.startswith(b):
                return True
            if not a.endswith("/") and b.startswith(a + "/"):
                return True
            if not b.endswith("/") and a.startswith(b + "/"):
                return True
    return False


def has_evidence_token(text: str) -> bool:
    return bool(EVIDENCE_TOKEN_RE.search(text))


def analyze_transcript(path: Path) -> Report:
    data = load_json(path)
    messages = extract_messages(data)
    delegates = extract_delegates(messages)
    findings: dict[tuple[str, int | None], Finding] = {}

    by_message: dict[int, list[Delegate]] = defaultdict(list)
    for delegate in delegates:
        by_message[delegate.message_index].append(delegate)

    root_start_message_index: int | None = None
    for message in messages:
        if START_CMD_RE.search(message.text):
            root_start_message_index = message.index
            break
        if normalize_speaker(message.speaker) == "start":
            root_start_message_index = message.index
            break

    if root_start_message_index is not None:
        saw_root_orchestrator = False

        for message in messages:
            if message.index < root_start_message_index:
                continue
            if normalize_speaker(message.speaker) != "start":
                continue

            delegates_in_message = by_message.get(message.index, [])
            if not delegates_in_message:
                if not saw_root_orchestrator and START_LOCAL_WORK_RE.search(message.text):
                    error(
                        findings,
                        "start_local_work_before_orchestrator",
                        "Root start performed local exploration or command-like work before Task(orchestrator) handoff.",
                        message.index,
                    )
                continue

            for delegate in delegates_in_message:
                if delegate.subagent == "orchestrator":
                    if (
                        has_prior_orchestrator_relay_request(messages, delegate.message_index)
                        and ORCHESTRATOR_RELAY_RESUME_RE.search(delegate.prompt)
                    ):
                        saw_root_orchestrator = True
                        continue
                    saw_root_orchestrator = True
                    if not orchestrator_prompt_has_original_request(delegate.prompt):
                        error(
                            findings,
                            "root_start_direct_orchestrator",
                            "Root start's Task(orchestrator) must include ORIGINAL_REQUEST (flattened handoff contract).",
                            delegate.message_index,
                        )
                    continue
                if delegate.subagent == "start":
                    continue
                if (
                    has_prior_orchestrator_relay_request(messages, delegate.message_index)
                    and ORCHESTRATOR_CHILD_PROXY_RE.search(delegate.prompt)
                ):
                    continue
                error(
                    findings,
                    "start_direct_specialist_without_orchestrator",
                    f'Root/start speaker delegated directly to "{delegate.subagent}" instead of Task(orchestrator) (or relay child proxy).',
                    delegate.message_index,
                )

        if not saw_root_orchestrator:
            error(
                findings,
                "root_start_missing_orchestrator",
                "Detected root /start flow but no Task(orchestrator) delegation from start with flattened handoff.",
                root_start_message_index,
            )

    for delegate in delegates:
        speaker = normalize_speaker(delegate.speaker)
        if speaker == "start" and delegate.subagent != "orchestrator":
            if (
                has_prior_orchestrator_relay_request(messages, delegate.message_index)
                and ORCHESTRATOR_CHILD_PROXY_RE.search(delegate.prompt)
            ):
                continue
            error(
                findings,
                "start_direct_specialist_without_orchestrator",
                f'Start speaker delegated to "{delegate.subagent}" instead of Task(orchestrator) (or relay child proxy).',
                delegate.message_index,
            )
        if delegate.subagent == "start":
            if is_supervised_worker_start(delegate.prompt):
                error(
                    findings,
                    "illegal_start_delegate",
                    "Task(start, supervised_worker / worker-start) is removed; use Task(orchestrator) with ORIGINAL_REQUEST from root start.",
                    delegate.message_index,
                )
            elif is_analyzer_start(delegate.prompt):
                if speaker != "orchestrator":
                    error(
                        findings,
                        "illegal_start_delegate",
                        'Task(start, analyzer) is allowed only from orchestrator.',
                        delegate.message_index,
                    )
            elif normalize_speaker(speaker) == "start":
                error(
                    findings,
                    "illegal_start_delegate",
                    "Root start must not delegate to Task(start); use Task(orchestrator) with ORIGINAL_REQUEST.",
                    delegate.message_index,
                )
            else:
                error(
                    findings,
                    "illegal_start_delegate",
                    'Task(start) is allowed only for analyzer handoffs from orchestrator.',
                    delegate.message_index,
                )

    for delegate in delegates:
        speaker = normalize_speaker(delegate.speaker)
        if speaker == "orchestrator" and delegate.subagent == "orchestrator":
            if ORCHESTRATOR_SELF_RECURSION_RE.search(delegate.prompt):
                error(
                    findings,
                    "illegal_orchestrator_recursion",
                    "Orchestrator must not spawn a full root-style Task(orchestrator) re-cycle (improper self-delegation).",
                    delegate.message_index,
                )

    for message in messages:
        delegates_in_message = by_message.get(message.index, [])
        if len(delegates_in_message) > 6:
            subagents = {delegate.subagent for delegate in delegates_in_message}
            if "orchestrator" not in subagents and "sub-orchestrator" not in message.text.lower():
                error(
                    findings,
                    "flat_fanout_overflow",
                    "More than 6 flat delegation branches were emitted without grouping under sub-orchestrators.",
                    message.index,
                )

        writer_delegates = [
            delegate for delegate in delegates_in_message if is_writer_agent(delegate.subagent)
        ]
        if len(writer_delegates) > 1:
            ownership_map: dict[int, list[str]] = {}
            missing_ownership = [
                delegate
                for delegate in writer_delegates
                if not ownership_tokens(extract_labeled_section(delegate.prompt, "OWNERSHIP"))
            ]
            if missing_ownership:
                agents = ", ".join(sorted({delegate.subagent for delegate in missing_ownership}))
                error(
                    findings,
                    "parallel_write_missing_ownership",
                    f"Parallel write-capable branches are missing explicit OWNERSHIP blocks: {agents}.",
                    message.index,
                )
            else:
                for idx, delegate in enumerate(writer_delegates):
                    section = extract_labeled_section(delegate.prompt, "OWNERSHIP")
                    ownership_map[idx] = ownership_tokens(section)

                overlaps: list[str] = []
                for (left_idx, left_delegate), (right_idx, right_delegate) in combinations(
                    list(enumerate(writer_delegates)),
                    2,
                ):
                    if ownership_sets_overlap(ownership_map[left_idx], ownership_map[right_idx]):
                        overlaps.append(
                            f"{left_delegate.subagent} vs {right_delegate.subagent}"
                        )
                if overlaps:
                    error(
                        findings,
                        "parallel_write_overlapping_ownership",
                        "Parallel writer branches have overlapping OWNERSHIP: "
                        + ", ".join(overlaps)
                        + ".",
                        message.index,
                    )

        same_type_counts = Counter(
            delegate.subagent for delegate in writer_delegates if delegate.subagent
        )
        for subagent, count in same_type_counts.items():
            if count >= 2:
                same_type = [
                    delegate
                    for delegate in writer_delegates
                    if delegate.subagent == subagent
                ]
                missing_same_type_ownership = [
                    delegate
                    for delegate in same_type
                    if not ownership_tokens(extract_labeled_section(delegate.prompt, "OWNERSHIP"))
                ]
                if missing_same_type_ownership:
                    error(
                        findings,
                        "same_type_missing_ownership",
                        f'Same-type delegation "{subagent} -> {subagent}" is missing explicit OWNERSHIP.',
                        message.index,
                    )

                if normalize_speaker(message.speaker) == subagent and count >= 3:
                    error(
                        findings,
                "same_type_fanout_needs_orchestrator",
                        f'Speaker "{subagent}" opened {count} same-type writer branches; escalate to orchestrator after 1-2 child writers.',
                        message.index,
                    )

    task_unavailable_indices = [
        message.index for message in messages if TASK_UNAVAILABLE_RE.search(message.text)
    ]
    if task_unavailable_indices:
        for message in messages:
            if message.index <= task_unavailable_indices[0]:
                continue
            if FAKE_ORCH_AFTER_UNAVAILABLE_RE.search(message.text):
                relay_marked = any(
                    RELAY_MARKER_RE.search(candidate.text)
                    or ORCHESTRATOR_RELAY_REQUEST_RE.search(candidate.text)
                    or ORCHESTRATOR_CHILD_PROXY_RE.search(candidate.text)
                    or ORCHESTRATOR_RELAY_RESUME_RE.search(candidate.text)
                    for candidate in messages
                    if task_unavailable_indices[0] < candidate.index <= message.index
                )
                if relay_marked:
                    continue
                error(
                    findings,
                    "task_unavailable_fake_orchestration",
                    "The transcript reports Task unavailability but continues as if real orchestration still ran.",
                    message.index,
                )
                break

    for message in messages:
        speaker = normalize_speaker(message.speaker)
        if speaker not in {"start", "orchestrator"}:
            continue
        legacy_status = LEGACY_RUNTIME_STATUS_RE.search(message.text)
        if legacy_status:
            error(
                findings,
                "legacy_runtime_status_used",
                f'Legacy runtime status "{legacy_status.group(1)}" used in active transcript output; use approval|pause|blocked|resume instead.',
                message.index,
            )

    resume_messages = [
        message
        for message in messages
        if STATUS_RESUME_RE.search(message.text) or RELAY_RESUME_TASK_RE.search(message.text)
    ]
    for message in resume_messages:
        has_prior_pause = any(
            candidate.index < message.index and PAUSE_STATE_RE.search(candidate.text)
            for candidate in messages
        )
        if not has_prior_pause:
            error(
                findings,
                "resume_without_prior_pause",
                "Resume transition was emitted without a prior paused/requested state in the transcript.",
                message.index,
            )
        if STATUS_RESUME_RE.search(message.text) and not EXPLICIT_RESUME_EVENT_RE.search(message.text):
            error(
                findings,
                "resume_without_explicit_event",
                "Runtime status resume requires an explicit resume_event (approval_granted/input_received/dependency_resolved).",
                message.index,
            )

    for message in messages:
        if not COMPLETION_CLAIM_RE.search(message.text):
            continue
        if "Task(subagent_type=" in message.text:
            continue
        if has_evidence_token(message.text):
            continue
        error(
            findings,
            "completion_claim_without_evidence",
            "Completion claim detected without explicit evidence token (path/check/output).",
            message.index,
        )

    full_text = "\n".join(message.text for message in messages)
    open_ended_until_stop = bool(
        root_start_message_index is not None
        and OPEN_ENDED_IMPROVEMENT_RE.search(full_text)
        and UNTIL_STOP_RE.search(full_text)
    )
    if open_ended_until_stop:
        has_steady_state_proof = bool(STEADY_STATE_PROOF_RE.search(full_text))
        has_pause_or_block = bool(PAUSE_OR_BLOCK_RE.search(full_text))

        stop_message = next(
            (
                message
                for message in messages
                if STATUS_DONE_RE.search(message.text) or RECOMMENDED_STOP_RE.search(message.text)
            ),
            None,
        )
        if stop_message and not has_steady_state_proof and not has_pause_or_block:
            error(
                findings,
                "open_ended_until_stop_premature_stop",
                "Open-ended until_user_stop improvement run stopped without steady_state proof, runtime pause, or blocker.",
                stop_message.index,
            )

        continue_without_next = next(
            (
                message
                for message in messages
                if STATUS_CONTINUE_RE.search(message.text) and NEXT_PACKET_NONE_RE.search(message.text)
            ),
            None,
        )
        if continue_without_next and not re.search(
            r"status\s*:\s*blocked\b",
            continue_without_next.text,
            re.IGNORECASE,
        ):
            error(
                findings,
                "open_ended_continue_without_next_packet",
                "Open-ended until_user_stop improvement run reported pause/continue but omitted a meaningful resume_packet for the next wave.",
                continue_without_next.index,
            )

    continuous_until_stop = bool(root_start_message_index is not None and UNTIL_STOP_RE.search(full_text))
    if continuous_until_stop:
        turn_boundary_continue = next(
            (
                message
                for message in messages
                if normalize_speaker(message.speaker) == "start"
                and TURN_BOUNDARY_CONTINUE_RE.search(message.text)
            ),
            None,
        )
        if turn_boundary_continue:
            has_auto_resume = any(
                message.index > turn_boundary_continue.index
                and normalize_speaker(message.speaker) == "start"
                and (
                    START_RESUME_TASK_RE.search(message.text)
                    or (
                        ORCHESTRATOR_TASK_RE.search(message.text)
                        and CONTINUOUS_ORCHESTRATOR_FOLLOWUP_RE.search(message.text)
                    )
                )
                for message in messages
            )
            if not has_auto_resume:
                error(
                    findings,
                    "continuous_missing_auto_resume",
                    "Continuous until_user_stop run hit runtime turn-boundary but did not auto-resume via Task(orchestrator) follow-up (CONTINUATION_PACKET / WAVE_NUMBER>1) or Task(start, resume=...).",
                    turn_boundary_continue.index,
                )

            if not WATCHDOG_BACKOFF_RE.search(full_text):
                error(
                    findings,
                    "continuous_missing_backoff_policy",
                    "Continuous until_user_stop run is missing retry/backoff watchdog evidence.",
                    turn_boundary_continue.index,
                )

            if not NO_PROGRESS_GUARD_RE.search(full_text):
                error(
                    findings,
                    "continuous_missing_no_progress_guard",
                    "Continuous until_user_stop run is missing no-progress guard evidence.",
                    turn_boundary_continue.index,
                )

            has_blocked_state = any(
                normalize_speaker(message.speaker) == "start"
                and re.search(r"status\s*:\s*blocked\b", message.text, re.IGNORECASE)
                for message in messages
            )
            if has_blocked_state and not BLOCKER_TAXONOMY_RE.search(full_text):
                error(
                    findings,
                    "continuous_missing_blocker_taxonomy",
                    "Blocked continuous run must include blocker taxonomy code (BLOCKED_RUNTIME/POLICY/INPUT/EXTERNAL/INTEGRATION).",
                )

    degraded_in_forbidden_context = bool(
        SINGLE_AGENT_DEGRADED_RE.search(full_text)
        and (root_start_message_index is not None or SWARM_OR_START_RE.search(full_text))
        and (UNTIL_STOP_RE.search(full_text) or OPEN_ENDED_IMPROVEMENT_RE.search(full_text) or SWARM_OR_START_RE.search(full_text))
    )
    if degraded_in_forbidden_context:
        degraded_message = next(
            (message for message in messages if SINGLE_AGENT_DEGRADED_RE.search(message.text)),
            None,
        )
        error(
            findings,
            "degraded_mode_forbidden_for_start_swarm",
            "SINGLE_AGENT_DEGRADED_MODE is forbidden for /start, swarm/24/7, and open-ended improvement flows; use relay or blocked/pause instead.",
            degraded_message.index if degraded_message else None,
        )

    analyzable_without_delegate = bool(task_unavailable_indices)

    if not delegates and root_start_message_index is None and not analyzable_without_delegate:
        status = "skipped"
    elif any(finding.severity == "error" for finding in findings.values()):
        status = "failed"
    else:
        status = "passed"

    ordered_findings = sorted(
        findings.values(),
        key=lambda finding: (finding.message_index is None, finding.message_index, finding.code),
    )
    return Report(
        path=path,
        status=status,
        messages=messages,
        delegates=delegates,
        findings=ordered_findings,
    )


def collect_json_inputs(paths: list[str]) -> list[Path]:
    collected: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_dir():
            collected.extend(sorted(child for child in path.rglob("*.json") if child.is_file()))
        elif path.is_file():
            collected.append(path)
        else:
            raise FileNotFoundError(f"Path does not exist: {raw_path}")
    return collected


def print_report(report: Report) -> None:
    print(f"Transcript report: {relative_label(report.path)}")
    print(f"- Messages: {len(report.messages)}")
    print(f"- Delegations: {len(report.delegates)}")
    print(f"- Status: {report.status}")
    if not report.findings:
        print("- Findings: none")
        return
    for finding in report.findings:
        location = (
            f"message {finding.message_index + 1}"
            if finding.message_index is not None
            else "global"
        )
        print(f"- [{finding.code}] {location}: {finding.message}")


def run_fixture_suite(case_file: Path) -> int:
    data = load_json(case_file)
    cases = data.get("cases", [])
    failures: list[str] = []
    passed = 0

    for case in cases:
        fixture_path = (case_file.parent / case["path"]).resolve()
        report = analyze_transcript(fixture_path)
        expected_status = case.get("expected_status", "pass")
        actual_status = "pass" if report.status == "passed" else "fail" if report.status == "failed" else "skip"
        if actual_status != expected_status:
            failures.append(
                f'[{case["id"]}] expected status {expected_status}, got {actual_status}'
            )

        present_codes = {finding.code for finding in report.findings}
        for code in case.get("required_findings", []):
            if code not in present_codes:
                failures.append(f'[{case["id"]}] missing expected finding "{code}"')
        for code in case.get("forbidden_findings", []):
            if code in present_codes:
                failures.append(f'[{case["id"]}] unexpected finding "{code}"')

        if actual_status == expected_status and not any(
            failure.startswith(f'[{case["id"]}]') for failure in failures
        ):
            passed += 1

    if failures:
        print("Transcript benchmarks failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Transcript benchmarks passed.")
    print(f"- Cases: {passed}")
    print(f"- Spec: {case_file.relative_to(ROOT).as_posix()}")
    return 0


def run_live(paths: list[str]) -> int:
    inputs = collect_json_inputs(paths)
    if not inputs:
        print("No transcript inputs found.", file=sys.stderr)
        return 1

    exit_code = 0
    for path in inputs:
        report = analyze_transcript(path.resolve())
        print_report(report)
        if report.status == "failed":
            exit_code = 1
    return exit_code


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate transcript/export JSON files for agent orchestration safety."
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="Transcript JSON files or directories. If omitted, run the committed fixture suite.",
    )
    parser.add_argument(
        "--case-file",
        default=str(DEFAULT_CASE_FILE),
        help="Fixture case spec to use when no inputs are provided.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.inputs:
        return run_live(args.inputs)
    return run_fixture_suite(Path(args.case_file).resolve())


if __name__ == "__main__":
    raise SystemExit(main())
