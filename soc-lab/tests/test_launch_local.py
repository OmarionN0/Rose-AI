"""Launcher regression tests: no subprocesses are started."""
import pytest
from tools import launch_local


def test_load_token_prefers_environment(tmp_path, monkeypatch):
    monkeypatch.setattr(launch_local, 'TOKEN_FILE', tmp_path / '.soc-token')
    monkeypatch.setenv('ROSE_SOC_TOKEN', 'x' * 40)
    assert launch_local.load_token() == 'x' * 40
    assert not (tmp_path / '.soc-token').exists()


def test_load_token_creates_local_secret(tmp_path, monkeypatch):
    monkeypatch.setattr(launch_local, 'TOKEN_FILE', tmp_path / '.soc-token')
    monkeypatch.delenv('ROSE_SOC_TOKEN', raising=False)
    first = launch_local.load_token()
    assert len(first) >= 32
    assert launch_local.load_token() == first
    assert (tmp_path / '.soc-token').read_text().strip() == first


def test_invalid_environment_token_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(launch_local, 'TOKEN_FILE', tmp_path / '.soc-token')
    monkeypatch.setenv('ROSE_SOC_TOKEN', 'short')
    with pytest.raises(ValueError):
        launch_local.load_token()


def test_commands_require_frontend_dependencies(monkeypatch, tmp_path):
    monkeypatch.setattr(launch_local, 'ROOT', tmp_path)
    monkeypatch.setattr(launch_local.shutil, 'which', lambda _: '/usr/bin/npm')
    with pytest.raises(RuntimeError, match='npm install'):
        launch_local.commands(False)
