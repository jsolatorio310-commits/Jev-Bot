import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.adapters import normalize_binance_rest, normalize_binance_websocket
from app.market import CandleStore


FIXTURES = Path(__file__).parents[1] / "app" / "fixtures"


def test_recorded_binance_fixtures_reproduce_same_candle() -> None:
    received = datetime(2026, 1, 1, 0, 30, tzinfo=timezone.utc)
    ws = normalize_binance_websocket(json.loads((FIXTURES / "binance_ws.json").read_text()), received)
    rest = normalize_binance_rest(json.loads((FIXTURES / "binance_rest.json").read_text())[0], "BTCUSDT", "15m", received)
    assert ws == rest


def test_unfinalized_candles_are_rejected() -> None:
    message = json.loads((FIXTURES / "binance_ws.json").read_text())
    message["k"]["x"] = False
    with pytest.raises(ValueError, match="finalized"):
        CandleStore().add(normalize_binance_websocket(message))


def test_sequence_gap_blocks_entries() -> None:
    message = json.loads((FIXTURES / "binance_ws.json").read_text())
    store = CandleStore()
    first = normalize_binance_websocket(message)
    assert store.add(first).blocks_entries is False
    message["k"]["f"] = 103
    message["k"]["t"] += 900000
    message["k"]["T"] += 900000
    second = normalize_binance_websocket(message)
    status = store.add(second)
    assert status.missing_sequences == [101, 102]
    assert status.blocks_entries is True
    message["k"]["f"] = 101
    message["k"]["t"] += 900000
    message["k"]["T"] += 900000
    store.add(normalize_binance_websocket(message))
    message["k"]["f"] = 102
    message["k"]["t"] += 900000
    message["k"]["T"] += 900000
    store.add(normalize_binance_websocket(message))
    latest_close = datetime.fromtimestamp(message["k"]["T"] / 1000, tz=timezone.utc)
    assert store.status("BTCUSDT", "15m", latest_close + timedelta(minutes=1)).blocks_entries is False


def test_stale_feed_blocks_entries() -> None:
    message = json.loads((FIXTURES / "binance_ws.json").read_text())
    store = CandleStore()
    candle = normalize_binance_websocket(message, datetime(2026, 1, 1, 0, 30, tzinfo=timezone.utc))
    store.add(candle)
    status = store.status("BTCUSDT", "15m", candle.close_time + timedelta(minutes=21))
    assert status.stale is True
    assert status.blocks_entries is True

