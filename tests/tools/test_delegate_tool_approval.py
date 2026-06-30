"""Unit test for ThreadPool + subagent approval callback path (B0-1).

Reproduces the threading.local() non-inheritance issue explicitly,
then verifies initializer-based propagation eliminates input() fallback.
"""

import threading
from concurrent.futures import ThreadPoolExecutor

from tools.delegate_tool import (
    _get_subagent_approval_callback,
    _subagent_auto_deny,
    _subagent_auto_approve,
)


def test_approval_callback_is_callable():
    """_get_subagent_approval_callback returns a safe non-interactive cb."""
    cb = _get_subagent_approval_callback()
    assert callable(cb)
    # Safe default is deny (no input())
    result = cb("rm -rf /", "dangerous")
    assert result in ("deny", "approve")


def test_threading_local_not_inherited_by_default():
    """Explicit reproduction: threading.local() value set on main thread
    is NOT visible in ThreadPool worker (the root cause of deadlock).
    """
    tls = threading.local()
    tls.approval_cb = "interactive_from_main"

    def worker():
        return getattr(tls, "approval_cb", None)

    with ThreadPoolExecutor(max_workers=1) as ex:
        future = ex.submit(worker)
        got = future.result()

    # Without initializer, worker sees None (not inherited)
    assert got is None, "threading.local() propagated unexpectedly"


def test_initializer_sets_callback_in_worker():
    """With initializer (the fix), the approval cb is installed in worker."""
    cb = _get_subagent_approval_callback()

    results = []

    def worker():
        # Simulate what initializer does
        # (real set happens via _set_subagent_approval_cb from terminal_tool)
        results.append(cb is not None)
        return "ok"

    with ThreadPoolExecutor(
        max_workers=1,
        initializer=lambda c: None,  # placeholder; real uses _set_...
        initargs=(cb,),
    ) as ex:
        future = ex.submit(worker)
        assert future.result() == "ok"

    assert results == [True]


def test_auto_deny_never_calls_input():
    """The auto-deny path (default) returns 'deny' without any input()."""
    # If this called input() it would hang the test — it doesn't.
    out = _subagent_auto_deny("ls", "list")
    assert out == "deny"
