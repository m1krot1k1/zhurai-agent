"""Best-effort Headroom proxy bootstrap for local Hermes sessions.

This module intentionally keeps bootstrap logic small and idempotent:
- Only loopback dashboard URLs are auto-managed.
- A healthy running proxy short-circuits immediately.
- Missing installation is handled via ``python -m pip install ...`` when enabled.
- Proxy start is backgrounded and health-checked with a bounded wait.
- A lightweight reverse proxy relays ``/dashboard`` from the old Headroom port
  (8787) to the real Hermes dashboard (9119) so legacy cross-references still work.
"""

from __future__ import annotations

import importlib.util
import json
import logging
import os
import platform
import shutil
import socket
import subprocess
import sys
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen, Request

from hermes_cli.config import load_config
from hermes_constants import get_hermes_home

logger = logging.getLogger(__name__)

_BOOTSTRAP_LOCK = threading.Lock()
_LAST_SUCCESS = False
_LAST_ATTEMPT_MONO = 0.0
_MIN_RETRY_SECONDS = 20.0

# The default port Headroom uses for its own proxy dashboard/stats/MCP UI.
_HEADROOM_PROXY_PORT = 8787
# The port where the real Hermes dashboard serves its web UI.
_HERMES_DASHBOARD_PORT = 9119
_HEADROOM_PROXY_URL = f"http://127.0.0.1:{_HEADROOM_PROXY_PORT}"


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


def _model_provider(config: Dict[str, Any]) -> str:
    model_cfg = config.get("model")
    if isinstance(model_cfg, dict):
        return str(model_cfg.get("provider") or "").strip().lower()
    return ""


def _desired_backend(provider: str) -> str:
    if provider in {"openrouter"}:
        return "openrouter"
    if provider in {"anthropic"}:
        return "anthropic"
    if provider in {"google", "gemini", "googleai"}:
        return "gemini"
    return ""


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


def _read_health(base_url: str, timeout_s: float = 1.0) -> Dict[str, Any]:
    try:
        with urlopen(f"{base_url.rstrip('/')}/health", timeout=timeout_s) as response:
            status = int(getattr(response, "status", 200))
            if not (200 <= status < 300):
                return {}
            payload = response.read().decode("utf-8", errors="replace")
            parsed = json.loads(payload)
            return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


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


def _resolve_start_command(backend: str = "") -> list[str]:
    backend_args = ["--backend", backend] if backend else []
    cli_path = shutil.which("headroom")
    if cli_path:
        return [cli_path, "proxy", *backend_args]
    if importlib.util.find_spec("headroom.cli") is not None:
        return [sys.executable, "-m", "headroom.cli", "proxy", *backend_args]
    return [sys.executable, "-m", "headroom", "proxy", *backend_args]


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


def _listeners_for_port(base_url: str) -> list[int]:
    _host, port = _host_port(base_url)
    try:
        proc = subprocess.run(
            ["lsof", "-nP", "-iTCP:%d" % port, "-sTCP:LISTEN", "-t"],
            capture_output=True,
            text=True,
            check=False,
            timeout=3,
        )
    except Exception:
        return []
    pids: list[int] = []
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            pids.append(int(line))
        except ValueError:
            continue
    return pids


def _kill_listeners(base_url: str) -> None:
    pids = _listeners_for_port(base_url)
    for pid in pids:
        try:
            os.kill(pid, 15)
        except Exception:
            continue
    if not pids:
        return
    deadline = time.monotonic() + 2.5
    while time.monotonic() < deadline:
        if not _port_is_open(base_url):
            return
        time.sleep(0.15)
    for pid in pids:
        try:
            os.kill(pid, 9)
        except Exception:
            continue


def _start_proxy(log_path: Path, backend: str = "") -> bool:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log_file:
        cmd = _resolve_start_command(backend=backend)
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


# ---------------------------------------------------------------------------
# Lightweight reverse proxy: /dashboard from port 8787 to real Hermes dashboard
# ---------------------------------------------------------------------------

_DASHBOARD_PROXY_SERVER: HTTPServer | None = None
_DASHBOARD_PROXY_THREAD: threading.Thread | None = None


class _DashboardForwardHandler(BaseHTTPRequestHandler):
    """HTTP request handler that forwards /dashboard/* requests to the real
    Hermes dashboard at 127.0.0.1:9119 and returns 404 for everything else."""

    def do_GET(self) -> None:
        self._forward()

    def do_POST(self) -> None:
        self._forward()

    def do_PUT(self) -> None:
        self._forward()

    def do_DELETE(self) -> None:
        self._forward()

    def do_HEAD(self) -> None:
        self._forward_no_body()

    def _target_url(self) -> str | None:
        """Build the target URL on the real Hermes dashboard, or None for
        non-dashboard paths that this proxy does not serve."""
        path = self.path
        if path.startswith("/dashboard"):
            return f"http://127.0.0.1:{_HERMES_DASHBOARD_PORT}{path}"
        # Also forward /api, /ws, /health — these are dashboard paths too
        # that the SPA and backend rely on.
        if path.startswith("/api/") or path.startswith("/ws") or path in ("/health", "/"):
            return f"http://127.0.0.1:{_HERMES_DASHBOARD_PORT}{path}"
        return None

    def _forward(self) -> None:
        target = self._target_url()
        if target is None:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")
            return

        body_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(body_length) if body_length > 0 else b""

        try:
            req = Request(
                target,
                data=body if body else None,
                headers={k: v for k, v in self.headers.items()
                         if k.lower() not in ("host", "content-length", "connection",
                                               "transfer-encoding")},
                method=self.command,
            )
            with urlopen(req, timeout=10.0) as upstream:
                self.send_response(int(upstream.status))
                for key, value in upstream.headers.items():
                    if key.lower() not in ("transfer-encoding", "content-encoding",
                                           "content-length", "connection"):
                        self.send_header(key, value)
                # Recompute content-length from the body we actually read
                upstream_body = upstream.read()
                self.send_header("Content-Length", str(len(upstream_body)))
                self.end_headers()
                self.wfile.write(upstream_body)
        except URLError as exc:
            logger.warning("Dashboard reverse proxy: upstream error for %s: %s", target, exc)
            self.send_response(502)
            self.end_headers()
            self.wfile.write(f"Proxy error: {exc}".encode())
        except Exception as exc:
            logger.warning("Dashboard reverse proxy: unexpected error for %s: %s", target, exc)
            self.send_response(502)
            self.end_headers()
            self.wfile.write(f"Proxy error: {exc}".encode())

    def _forward_no_body(self) -> None:
        target = self._target_url()
        if target is None:
            self.send_response(404)
            self.end_headers()
            return
        try:
            req = Request(target, method="HEAD")
            with urlopen(req, timeout=5.0) as upstream:
                self.send_response(int(upstream.status))
                for key, value in upstream.headers.items():
                    if key.lower() not in ("transfer-encoding", "content-encoding",
                                           "content-length", "connection"):
                        self.send_header(key, value)
                self.end_headers()
        except URLError:
            self.send_response(502)
            self.end_headers()

    def log_message(self, fmt: str, *args: Any) -> None:
        logger.debug("Dashboard reverse proxy: %s", fmt % args)


def _start_dashboard_reverse_proxy() -> bool:
    """Start a lightweight HTTP reverse proxy on port 8787 that forwards
    `/dashboard`, `/api/`, `/ws`, and `/health` requests to the real Hermes
    dashboard at 127.0.0.1:9119.

    This ensures that any code, tool, or integration that still hits the old
    Headroom dashboard URL (http://127.0.0.1:8787/dashboard) gets seamlessly
    forwarded to the actual dashboard.
    """
    global _DASHBOARD_PROXY_SERVER, _DASHBOARD_PROXY_THREAD

    if _DASHBOARD_PROXY_THREAD is not None and _DASHBOARD_PROXY_THREAD.is_alive():
        return True

    try:
        with socket.create_connection(("127.0.0.1", _HEADROOM_PROXY_PORT), timeout=0.3):
            logger.debug(
                "Dashboard reverse proxy: port %d already in use — skipping",
                _HEADROOM_PROXY_PORT,
            )
            return True
    except OSError:
        pass

    try:
        server = HTTPServer(("127.0.0.1", _HEADROOM_PROXY_PORT), _DashboardForwardHandler)
        _DASHBOARD_PROXY_SERVER = server
        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True,
            name="dashboard-reverse-proxy",
        )
        thread.start()
        _DASHBOARD_PROXY_THREAD = thread
        logger.info(
            "Dashboard reverse proxy: forwarding http://127.0.0.1:%d/dashboard -> "
            "http://127.0.0.1:%d/dashboard",
            _HEADROOM_PROXY_PORT,
            _HERMES_DASHBOARD_PORT,
        )
        return True
    except OSError as exc:
        logger.warning(
            "Dashboard reverse proxy: failed to bind port %d: %s",
            _HEADROOM_PROXY_PORT,
            exc,
        )
        return False


# ---------------------------------------------------------------------------
# Config auto-fix: detect dashboard_url pointing to Headroom's own port
# ---------------------------------------------------------------------------

def _fix_dashboard_url_if_wrong(hcfg: Dict[str, Any]) -> str:
    """Detect if dashboard_url points to Headroom's own proxy port and
    auto-correct it to the real Hermes dashboard port with a warning.

    Returns the corrected (or original) dashboard URL.
    """
    url = _dashboard_url(hcfg)
    if not url:
        return url

    parsed = urlparse(url)
    if parsed.port == _HEADROOM_PROXY_PORT:
        corrected = f"http://127.0.0.1:{_HERMES_DASHBOARD_PORT}"
        logger.warning(
            "headroom.dashboard_url is set to Headroom's own proxy port "
            "(%s). Auto-correcting to Hermes dashboard (%s). "
            "Persisting fix to config.yaml.",
            url,
            corrected,
        )
        try:
            from hermes_cli.config import load_config, save_config
            cfg = load_config()
            if isinstance(cfg.get("headroom"), dict):
                cfg["headroom"]["dashboard_url"] = corrected
                save_config(cfg)
                logger.info("Persisted dashboard_url fix to config.yaml: %s", corrected)
        except Exception as exc:
            logger.warning("Could not persist dashboard_url fix to config: %s", exc)
        return corrected

    if parsed.port == _HERMES_DASHBOARD_PORT:
        return url

    return url


def ensure_headroom_proxy_started() -> Dict[str, Any]:
    """Ensure local Headroom proxy is up (best effort, no hard failures)."""
    global _LAST_ATTEMPT_MONO, _LAST_SUCCESS

    with _BOOTSTRAP_LOCK:
        config = load_config()
        hcfg = config.get("headroom") if isinstance(config.get("headroom"), dict) else {}
        if not _bool(hcfg, "enabled", True):
            return {"status": "disabled"}

        # Auto-fix dashboard_url if it points to Headroom's own proxy port (8787).
        base_url = _fix_dashboard_url_if_wrong(hcfg)
        # If the auto-fix persisted a config change, reload hcfg.
        if base_url != _dashboard_url(hcfg):
            config = load_config()
            hcfg = config.get("headroom") if isinstance(config.get("headroom"), dict) else {}

        # Start a lightweight reverse proxy on port 8787 so any code still
        # hitting the old Headroom dashboard URL gets forwarded to the real
        # Hermes dashboard on port 9119.
        _start_dashboard_reverse_proxy()

        desired_backend = _desired_backend(_model_provider(config))
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not _is_loopback(parsed.hostname or ""):
            return {"status": "skipped_non_loopback", "base_url": base_url}

        if _is_healthy(base_url):
            if desired_backend:
                health = _read_health(base_url, timeout_s=1.0)
                actual_backend = str(
                    ((health.get("config") or {}) if isinstance(health.get("config"), dict) else {}).get("backend")
                    or ""
                ).strip().lower()
                if actual_backend and actual_backend != desired_backend:
                    _kill_listeners(base_url)
                    time.sleep(0.4)
                    if _is_healthy(base_url, timeout_s=0.8):
                        return {"status": "backend_mismatch_unresolved", "base_url": base_url}
                else:
                    _LAST_SUCCESS = True
                    return {"status": "healthy", "base_url": base_url}
            else:
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
            _start_proxy(log_file, backend=desired_backend)
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


def routed_headroom_base_url(*, provider: str, api_mode: str, base_url: str) -> str:
    """Return proxy-routed base URL when headroom request routing is enabled."""
    config = load_config()
    hcfg = config.get("headroom") if isinstance(config.get("headroom"), dict) else {}
    if not _bool(hcfg, "enabled", True) or not _bool(hcfg, "route_model_requests", True):
        return base_url

    provider_norm = str(provider or "").strip().lower()
    mode = str(api_mode or "").strip().lower()
    base_norm = str(base_url or "").strip().lower()

    # Skip only runtimes that are not OpenAI/Anthropic HTTP transports and
    # therefore cannot be proxied through Headroom's request router.
    if provider_norm in {"bedrock", "copilot-acp"}:
        return base_url
    if mode in {"bedrock_converse", "codex_app_server"}:
        return base_url
    if base_norm.startswith("acp://") or base_norm.startswith("acp+tcp://"):
        return base_url

    dashboard = _dashboard_url(hcfg)
    if not dashboard:
        return base_url

    clean = str(base_url or "").strip().rstrip("/")
    if clean.startswith(dashboard):
        return clean

    if mode == "anthropic_messages":
        return dashboard
    return f"{dashboard}/v1"
