"""Preflight diagnostics should not disclose credentials or local identifiers."""
import os
from tools import check_local_setup


def test_preflight_never_prints_token(monkeypatch, capsys):
    secret = "synthetic-secret-" + "x" * 40
    monkeypatch.setenv("ROSE_SOC_TOKEN", secret)
    monkeypatch.setattr(check_local_setup, "port_state", lambda _: False)
    check_local_setup.main()
    output = capsys.readouterr().out
    assert secret not in output
    assert "Token environment: configured" in output
    assert "API port 8000: available" in output


def test_preflight_detects_missing_token(monkeypatch, capsys):
    monkeypatch.delenv("ROSE_SOC_TOKEN", raising=False)
    monkeypatch.setattr(check_local_setup, "port_state", lambda _: False)
    check_local_setup.main()
    assert "Token environment: not configured" in capsys.readouterr().out
