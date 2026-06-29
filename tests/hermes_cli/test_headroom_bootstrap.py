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
