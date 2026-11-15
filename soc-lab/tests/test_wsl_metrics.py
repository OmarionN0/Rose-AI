"""Unit tests for WSL2 aggregate CPU and memory calculations."""
from collector import wsl_metrics


def test_memory_percent_reads_only_aggregate_values(monkeypatch):
    class FakePath:
        def __init__(self, path):
            self.path = path
        def read_text(self):
            return "MemTotal: 1000 kB\nMemAvailable: 250 kB\n"
    monkeypatch.setattr(wsl_metrics, "Path", FakePath)
    assert wsl_metrics.memory_percent() == 75.0


def test_cpu_sampling_calculates_non_idle_percentage(monkeypatch):
    readings = iter([(100, 50), (200, 70)])
    monkeypatch.setattr(wsl_metrics, "cpu_ticks", lambda: next(readings))
    monkeypatch.setattr(wsl_metrics, "memory_percent", lambda: 40.0)
    monkeypatch.setattr(wsl_metrics.time, "sleep", lambda _: None)
    assert wsl_metrics.sample(1) == {"cpu_percent": 80.0, "memory_percent": 40.0}


def test_cpu_sampling_handles_no_elapsed_ticks(monkeypatch):
    monkeypatch.setattr(wsl_metrics, "cpu_ticks", lambda: (100, 50))
    monkeypatch.setattr(wsl_metrics, "memory_percent", lambda: 12.0)
    monkeypatch.setattr(wsl_metrics.time, "sleep", lambda _: None)
    assert wsl_metrics.sample(1)["cpu_percent"] == 0.0
