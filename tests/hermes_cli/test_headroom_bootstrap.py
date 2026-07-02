from hermes_cli import headroom_bootstrap as hb


def _reset_state() -> None:
    hb._LAST_ATTEMPT_MONO = 0.0
    hb._LAST_SUCCESS = False


def test_headroom_bootstrap_skips_non_loopback(monkeypatch):
    _reset_state()
    monkeypatch.setattr(
        hb,
        "load_config",
        lambda: {"headroom": {"enabled": True, "dashboard_url": "https://example.com:8787"}},
    )

    result = hb.ensure_headroom_proxy_started()

    assert result["status"] == "skipped_non_loopback"


def test_headroom_bootstrap_reports_missing_binary_when_auto_install_off(monkeypatch):
    _reset_state()
    monkeypatch.setattr(
        hb,
        "load_config",
        lambda: {
            "headroom": {
                "enabled": True,
                "dashboard_url": "http://127.0.0.1:8787",
                "auto_install": False,
            },
        },
    )
    monkeypatch.setattr(hb, "_is_healthy", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(hb, "_headroom_available", lambda: False)

    result = hb.ensure_headroom_proxy_started()

    assert result["status"] == "missing_binary"


def test_headroom_bootstrap_short_circuits_when_healthy(monkeypatch):
    _reset_state()
    monkeypatch.setattr(
        hb,
        "load_config",
        lambda: {"headroom": {"enabled": True, "dashboard_url": "http://127.0.0.1:8787"}},
    )
    monkeypatch.setattr(hb, "_is_healthy", lambda *_args, **_kwargs: True)

    result = hb.ensure_headroom_proxy_started()

    assert result["status"] == "healthy"


def test_is_healthy_accepts_2xx_status(monkeypatch):
    class _Resp:
        status = 204

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    monkeypatch.setattr(hb, "urlopen", lambda *_args, **_kwargs: _Resp())

    assert hb._is_healthy("http://127.0.0.1:8787") is True


def test_is_healthy_rejects_non_2xx_status(monkeypatch):
    class _Resp:
        status = 404

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    monkeypatch.setattr(hb, "urlopen", lambda *_args, **_kwargs: _Resp())

    assert hb._is_healthy("http://127.0.0.1:8787") is False


def test_resolve_start_command_prefers_headroom_cli_binary(monkeypatch):
    monkeypatch.setattr(hb.shutil, "which", lambda name: "/tmp/headroom" if name == "headroom" else None)

    assert hb._resolve_start_command() == ["/tmp/headroom", "proxy"]


def test_resolve_start_command_falls_back_to_headroom_cli_module(monkeypatch):
    monkeypatch.setattr(hb.shutil, "which", lambda _name: None)
    monkeypatch.setattr(
        hb.importlib.util,
        "find_spec",
        lambda name: object() if name == "headroom.cli" else None,
    )

    assert hb._resolve_start_command() == [hb.sys.executable, "-m", "headroom.cli", "proxy"]


def test_ensure_pip_uses_ensurepip_when_missing(monkeypatch):
    class _Proc:
        def __init__(self, rc: int):
            self.returncode = rc
            self.stdout = ""
            self.stderr = ""

    calls = []

    def _fake_run(cmd, **_kwargs):
        calls.append(cmd)
        if cmd[:3] == [hb.sys.executable, "-m", "pip"]:
            return _Proc(1)
        if cmd[:3] == [hb.sys.executable, "-m", "ensurepip"]:
            return _Proc(0)
        return _Proc(0)

    monkeypatch.setattr(hb.subprocess, "run", _fake_run)

    assert hb._ensure_pip(30.0) is True
    assert any(cmd[:3] == [hb.sys.executable, "-m", "ensurepip"] for cmd in calls)


def test_headroom_bootstrap_skips_duplicate_spawn_when_port_already_open(monkeypatch):
    _reset_state()
    monkeypatch.setattr(
        hb,
        "load_config",
        lambda: {"headroom": {"enabled": True, "dashboard_url": "http://127.0.0.1:8787"}},
    )
    monkeypatch.setattr(hb, "_is_healthy", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(hb, "_headroom_available", lambda: True)
    monkeypatch.setattr(hb, "_port_is_open", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(hb.time, "sleep", lambda *_args, **_kwargs: None)
    started = {"called": False}
    monkeypatch.setattr(hb, "_start_proxy", lambda *_args, **_kwargs: started.__setitem__("called", True))

    result = hb.ensure_headroom_proxy_started()

    assert result["status"] == "port_in_use_unhealthy"
    assert started["called"] is False


def test_routed_headroom_base_url_routes_chat_modes(monkeypatch):
    monkeypatch.setattr(
        hb,
        "load_config",
        lambda: {
            "headroom": {
                "enabled": True,
                "route_model_requests": True,
                "dashboard_url": "http://127.0.0.1:8787",
            },
        },
    )
    routed = hb.routed_headroom_base_url(
        provider="openrouter",
        api_mode="chat_completions",
        base_url="https://openrouter.ai/api/v1",
    )
    assert routed == "http://127.0.0.1:8787/v1"


def test_routed_headroom_base_url_routes_anthropic_mode(monkeypatch):
    monkeypatch.setattr(
        hb,
        "load_config",
        lambda: {
            "headroom": {
                "enabled": True,
                "route_model_requests": True,
                "dashboard_url": "http://127.0.0.1:8787",
            },
        },
    )
    routed = hb.routed_headroom_base_url(
        provider="anthropic",
        api_mode="anthropic_messages",
        base_url="https://api.anthropic.com",
    )
    assert routed == "http://127.0.0.1:8787"


def test_routed_headroom_base_url_routes_custom_provider(monkeypatch):
    monkeypatch.setattr(
        hb,
        "load_config",
        lambda: {
            "headroom": {
                "enabled": True,
                "route_model_requests": True,
                "dashboard_url": "http://127.0.0.1:8787",
            },
        },
    )
    original = "http://localhost:11434/v1"
    routed = hb.routed_headroom_base_url(
        provider="custom",
        api_mode="chat_completions",
        base_url=original,
    )
    assert routed == "http://127.0.0.1:8787/v1"


def test_routed_headroom_base_url_skips_bedrock_runtime(monkeypatch):
    monkeypatch.setattr(
        hb,
        "load_config",
        lambda: {
            "headroom": {
                "enabled": True,
                "route_model_requests": True,
                "dashboard_url": "http://127.0.0.1:8787",
            },
        },
    )
    original = "https://bedrock-runtime.us-east-1.amazonaws.com"
    routed = hb.routed_headroom_base_url(
        provider="bedrock",
        api_mode="bedrock_converse",
        base_url=original,
    )
    assert routed == original


def test_routed_headroom_base_url_skips_codex_app_server(monkeypatch):
    monkeypatch.setattr(
        hb,
        "load_config",
        lambda: {
            "headroom": {
                "enabled": True,
                "route_model_requests": True,
                "dashboard_url": "http://127.0.0.1:8787",
            },
        },
    )
    original = "acp://copilot"
    routed = hb.routed_headroom_base_url(
        provider="copilot-acp",
        api_mode="codex_app_server",
        base_url=original,
    )
    assert routed == original


# ---------------------------------------------------------------------------
# _fix_dashboard_url_if_wrong: auto-correct a stale dashboard_url pointing at
# the Hermes web dashboard port (9119) back to the Headroom proxy port (8787).
# This is the migration path for configs written by the prior regression that
# flipped the default to 9119 — without it, model API routing silently breaks
# in CLI/TUI/desktop modes (only an explicitly-running dashboard masked it).
# ---------------------------------------------------------------------------


def test_fix_dashboard_url_corrects_dashboard_port_to_proxy_port(monkeypatch):
    """A dashboard_url on 9119 is rewritten to 8787 and persisted."""
    persisted = {}

    monkeypatch.setattr(
        hb,
        "load_config",
        lambda: {"headroom": {"dashboard_url": "http://127.0.0.1:9119"}},
    )

    def _save(cfg):
        persisted["url"] = cfg["headroom"]["dashboard_url"]

    monkeypatch.setattr("hermes_cli.config.save_config", _save)

    corrected = hb._fix_dashboard_url_if_wrong({"dashboard_url": "http://127.0.0.1:9119"})

    assert corrected == "http://127.0.0.1:8787"
    assert persisted.get("url") == "http://127.0.0.1:8787"


def test_fix_dashboard_url_leaves_correct_proxy_port_alone(monkeypatch):
    """A dashboard_url already on 8787 is returned unchanged (no rewrite/persist)."""
    monkeypatch.setattr(
        hb,
        "load_config",
        lambda: {"headroom": {"dashboard_url": "http://127.0.0.1:8787"}},
    )

    result = hb._fix_dashboard_url_if_wrong({"dashboard_url": "http://127.0.0.1:8787"})
    assert result == "http://127.0.0.1:8787"
