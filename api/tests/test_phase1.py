import pytest
from pathlib import Path

from app.contracts import LedgerEvent
from app.ledger import Ledger
from app.replay import load_fixture


def test_replay_fixture_round_trips() -> None:
    record = load_fixture(Path(__file__).parents[1] / "fixtures" / "replay.json")
    assert record.decision.snapshot_id == record.snapshot.snapshot_id
    assert record.model_validate_json(record.model_dump_json()) == record


def test_duplicate_event_key_is_rejected() -> None:
    ledger = Ledger()
    event = LedgerEvent(event_key="balance:1", event_type="balance", payload={"asset": "USDT", "delta": 100})
    ledger.append(event)
    with pytest.raises(Exception):
        ledger.append(event.model_copy(update={"event_id": event.event_id}))


def test_restart_rebuilds_known_portfolio(tmp_path) -> None:
    path = tmp_path / "ledger.db"
    ledger = Ledger(path)
    ledger.append(LedgerEvent(event_key="balance:1", event_type="balance", payload={"asset": "USDT", "delta": 1000}))
    ledger.append(LedgerEvent(event_key="position:1", event_type="position", payload={"symbol": "BTC/USDT", "quantity_delta": 0.1, "average_price": 10000}))
    ledger.db.close()

    restarted = Ledger(path)
    assert restarted.rebuild() == {
        "balances": {"USDT": 1000},
        "positions": {"BTC/USDT": {"quantity": 0.1, "average_price": 10000}},
    }

