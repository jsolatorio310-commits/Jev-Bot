import pytest
from fastapi.testclient import TestClient

from app.config import load_settings
from app.main import app, state

client = TestClient(app)


def setup_function() -> None:
    state.emergency_stopped = False


def test_config_is_paper_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAPER_ONLY", "true")
    assert load_settings().paper_only is True


def test_config_rejects_live_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAPER_ONLY", "false")
    with pytest.raises(RuntimeError, match="PAPER_ONLY"):
        load_settings()


def test_emergency_stop_is_visible_in_health() -> None:
    assert client.get("/health").json()["emergency_stopped"] is False
    assert client.post("/controls/emergency-stop").json() == {"emergency_stopped": True}
    assert client.get("/health").json()["emergency_stopped"] is True


def test_resume_requires_an_active_stop() -> None:
    assert client.post("/controls/resume").status_code == 409
    client.post("/controls/emergency-stop")
    assert client.post("/controls/resume").json() == {"emergency_stopped": False}

