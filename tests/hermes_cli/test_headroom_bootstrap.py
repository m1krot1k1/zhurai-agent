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
            }
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
