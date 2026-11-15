from tools.vulnerability_report import render
import pytest

def test_offline_report():
    report = render({"assets": [{"asset": "synthetic-pi", "severity": "unknown"}]})
    assert "synthetic-pi" in report
    assert "Unverified" in report

def test_reject_invalid_cve():
    with pytest.raises(ValueError):
        render({"assets": [{"cve": "not-a-cve"}]})

def test_reject_invalid_entries():
    with pytest.raises(ValueError):
        render({"assets": "bad"})
