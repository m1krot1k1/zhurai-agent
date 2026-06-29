"""Best-effort Headroom proxy bootstrap for local Hermes sessions.

This module intentionally keeps bootstrap logic small and idempotent:
- Only loopback dashboard URLs are auto-managed.
- A healthy running proxy short-circuits immediately.
- Missing installation is handled via ``python -m pip install ...`` when enabled.
- Proxy start is backgrounded and health-checked with a bounded wait.
"""

from __future__ import annotations

import importlib.util
import logging
import os
import platform
import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

from hermes_cli.config import load_config
from hermes_constants import get_hermes_home

logger = logging.getLogger(__name__)

_BOOTSTRAP_LOCK = threading.Lock()
_LAST_SUCCESS = False
_LAST_ATTEMPT_MONO = 0.0
_MIN_RETRY_SECONDS = 20.0


def _bool(cfg: Dict[str, Any], key: str, default: bool) -> bool:
    value = cfg.get(key, default)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return default


def _number(cfg: Dict[str, Any], key: str, default: float) -> float:
    value = cfg.get(key, default)
    try:
        parsed = float(value)
        if parsed > 0:
            return parsed
    except Exception:
        pass
    return default


def _dashboard_url(cfg: Dict[str, Any]) -> str:
    raw = str(cfg.get("dashboard_url") or "http://127.0.0.1:8787").strip()
    return raw.rstrip("/")


def _is_loopback(hostname: str) -> bool:
    host = (hostname or "").lower().rstrip(".")
    return host in {"localhost", "127.0.0.1", "::1", "0.0.0.0"}


def _health_url(base_url: str) -> str:
    return f"{base_url.rstrip('/')}/stats"


def _is_healthy(base_url: str, timeout_s: float = 1.0) -> bool:
    try:
        with urlopen(_health_url(base_url), timeout=timeout_s) as response:
            status = int(getattr(response, "status", 200))
            return 200 <= status < 300
    except (URLError, TimeoutError, OSError):
        return False


def _headroom_available() -> bool:
    if shutil.which("headroom"):
        return True
    return importlib.util.find_spec("headroom") is not None


def _ensure_pip(timeout_s: float) -> bool:
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=max(timeout_s, 10.0),
        )
    except Exception:
        proc = None
    if proc is not None and proc.returncode == 0:
        return True

    logger.info("Headroom bootstrap: pip missing, running ensurepip")
    try:
        ensure_proc = subprocess.run(
            [sys.executable, "-m", "ensurepip", "--upgrade"],
            check=False,
            capture_output=True,
            text=True,
            timeout=max(timeout_s, 20.0),
        )
    except Exception as exc:
        logger.warning("Headroom bootstrap: ensurepip failed to start: %s", exc)
        return False
    if ensure_proc.returncode != 0:
        logger.warning(
            "Headroom bootstrap: ensurepip failed (rc=%s): %s",
            ensure_proc.returncode,
            (ensure_proc.stderr or ensure_proc.stdout or "").strip()[:1000],
        )
        return False
    return True


def _run_install(timeout_s: float) -> bool:
    if not _ensure_pip(timeout_s):
        return False
    cmd = [sys.executable, "-m", "pip", "install", "headroom-ai[proxy,mcp]"]
    logger.info("Headroom bootstrap: installing package via pip")
    try:
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=max(timeout_s, 30.0),
        )
    except Exception as exc:
        logger.warning("Headroom bootstrap: install failed to start: %s", exc)
        return False
    if proc.returncode != 0:
        logger.warning(
            "Headroom bootstrap: pip install failed (rc=%s): %s",
            proc.returncode,
            (proc.stderr or proc.stdout or "").strip()[:1000],
        )
        return False
    return _headroom_available()


def _resolve_start_command() -> list[str]:
    cli_path = shutil.which("headroom")
    if cli_path:
        return [cli_path, "proxy"]
    if importlib.util.find_spec("headroom.cli") is not None:
        return [sys.executable, "-m", "headroom.cli", "proxy"]
    return [sys.executable, "-m", "headroom", "proxy"]


def _host_port(base_url: str) -> tuple[str, int]:
    parsed = urlparse(base_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port
    if port is None:
        port = 443 if parsed.scheme == "https" else 80
    return host, port


def _port_is_open(base_url: str, timeout_s: float = 0.5) -> bool:
    host, port = _host_port(base_url)
    try:
        with socket.create_connection((host, port), timeout=timeout_s):
            return True
    except OSError:
        return False


def _start_proxy(log_path: Path) -> bool:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log_file:
        cmd = _resolve_start_command()
        kwargs: Dict[str, Any] = {
            "stdout": log_file,
            "stderr": subprocess.STDOUT,
            "stdin": subprocess.DEVNULL,
            "close_fds": True,
        }
        if platform.system() != "Windows":
            kwargs["preexec_fn"] = os.setsid  # detached process group  # windows-footgun: ok
        subprocess.Popen(cmd, **kwargs)
    return True


def ensure_headroom_proxy_started() -> Dict[str, Any]:
    """Ensure local Headroom proxy is up (best effort, no hard failures)."""
    global _LAST_ATTEMPT_MONO, _LAST_SUCCESS

    with _BOOTSTRAP_LOCK:
        config = load_config()
        hcfg = config.get("headroom") if isinstance(config.get("headroom"), dict) else {}
        if not _bool(hcfg, "enabled", True):
            return {"status": "disabled"}

        base_url = _dashboard_url(hcfg)
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not _is_loopback(parsed.hostname or ""):
            return {"status": "skipped_non_loopback", "base_url": base_url}

        if _is_healthy(base_url):
            _LAST_SUCCESS = True
            return {"status": "healthy", "base_url": base_url}

        now = time.monotonic()
        if _LAST_ATTEMPT_MONO and (now - _LAST_ATTEMPT_MONO) < _MIN_RETRY_SECONDS:
            return {"status": "cooldown", "base_url": base_url}
        _LAST_ATTEMPT_MONO = now

        auto_install = _bool(hcfg, "auto_install", True)
        auto_start = _bool(hcfg, "auto_start", True)
        install_timeout = _number(hcfg, "install_timeout_seconds", 180.0)
        start_timeout = _number(hcfg, "startup_timeout_seconds", 8.0)

        if not _headroom_available():
            if not auto_install:
                return {"status": "missing_binary", "base_url": base_url}
            if not _run_install(install_timeout):
                return {"status": "install_failed", "base_url": base_url}

        if not auto_start:
            return {"status": "ready_not_started", "base_url": base_url}

        # If something is already binding this port, avoid spawning duplicates.
        if _port_is_open(base_url):
            deadline = time.monotonic() + start_timeout
            while time.monotonic() < deadline:
                if _is_healthy(base_url, timeout_s=1.0):
                    _LAST_SUCCESS = True
                    return {"status": "healthy", "base_url": base_url}
                time.sleep(0.4)
            return {"status": "port_in_use_unhealthy", "base_url": base_url}

        log_file = get_hermes_home() / "logs" / "headroom-proxy.log"
        try:
            _start_proxy(log_file)
        except Exception as exc:
            logger.warning("Headroom bootstrap: failed to start proxy: %s", exc)
            return {"status": "start_failed", "base_url": base_url}

        deadline = time.monotonic() + start_timeout
        while time.monotonic() < deadline:
            if _is_healthy(base_url, timeout_s=1.0):
                _LAST_SUCCESS = True
                return {"status": "started", "base_url": base_url}
            time.sleep(0.4)

        return {"status": "start_timeout", "base_url": base_url}
