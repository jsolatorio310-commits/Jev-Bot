from datetime import datetime, timezone

from .market import Candle


def _time(value: int | float) -> datetime:
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc)


def normalize_binance_websocket(message: dict, received_at: datetime | None = None) -> Candle:
    event = message["k"]
    return Candle(
        exchange="binance",
        symbol=event["s"],
        interval=event["i"],
        open_time=_time(event["t"]),
        close_time=_time(event["T"]),
        received_at=received_at or datetime.now(timezone.utc),
        open=float(event["o"]),
        high=float(event["h"]),
        low=float(event["l"]),
        close=float(event["c"]),
        volume=float(event["v"]),
        sequence=int(event["f"]),
        finalized=bool(event["x"]),
    )


def normalize_binance_rest(row: list, symbol: str, interval: str, received_at: datetime | None = None) -> Candle:
    return Candle(
        exchange="binance",
        symbol=symbol,
        interval=interval,
        open_time=_time(row[0]),
        close_time=_time(row[6]),
        received_at=received_at or datetime.now(timezone.utc),
        open=float(row[1]),
        high=float(row[2]),
        low=float(row[3]),
        close=float(row[4]),
        volume=float(row[5]),
        sequence=int(row[8]),
        finalized=True,
    )

