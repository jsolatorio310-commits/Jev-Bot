from datetime import datetime, timedelta, timezone

from app.strategy import Bar, Position, RiskLimits, atr, ema, evaluate


def bars(count: int, start: float, step: float = 1) -> list[Bar]:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [Bar(timestamp=base + timedelta(minutes=15 * i), open=start + step * i, high=start + step * i + 1, low=start + step * i - 1, close=start + step * i) for i in range(count)]


def test_indicators_require_history() -> None:
    assert ema([1, 2], 3) is None
    assert atr(bars(14, 100), 14) is None


def test_bullish_trend_without_reclaim_is_no_fit() -> None:
    intraday = bars(30, 100)
    hourly = bars(200, 100)
    assert evaluate(intraday, hourly, RiskLimits(equity=10_000)).action == "HOLD"


def test_stop_target_and_expiry_exits() -> None:
    intraday = bars(30, 100)
    opened = intraday[-1].timestamp
    position = Position(entry=100, quantity=1, stop=99, target=101, opened_at=opened)
    assert evaluate(intraday[:-1] + [intraday[-1].model_copy(update={"low": 98})], bars(200, 100), RiskLimits(equity=10_000), position).reasons == ["stop hit"]
    assert evaluate(intraday[:-1] + [intraday[-1].model_copy(update={"high": 102})], bars(200, 100), RiskLimits(equity=10_000), position).reasons == ["target hit"]
    quiet = intraday[-1].model_copy(update={"high": 100.5, "low": 99.5})
    assert evaluate(intraday[:-1] + [quiet], bars(200, 100), RiskLimits(equity=10_000), position, opened + timedelta(hours=4)).reasons == ["expiry reached"]


def test_no_lookahead_changes_prior_result() -> None:
    intraday = bars(30, 100)
    hourly = bars(200, 100)
    before = evaluate(intraday, hourly, RiskLimits(equity=10_000))
    after = evaluate(intraday, hourly + bars(1, 10_000, 0), RiskLimits(equity=10_000))
    assert before == after

