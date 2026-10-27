from datetime import datetime, timedelta, timezone
from typing import Literal

from pydantic import BaseModel, Field


class Candle(BaseModel):
    exchange: str
    symbol: str
    interval: Literal["15m"]
    open_time: datetime
    close_time: datetime
    received_at: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    sequence: int
    finalized: bool


class FeedStatus(BaseModel):
    stale: bool
    gap_detected: bool
    blocks_entries: bool
    expected_sequence: int | None = None
    missing_sequences: list[int] = Field(default_factory=list)


class CandleStore:
    def __init__(self, stale_after: timedelta = timedelta(minutes=20)):
        self.stale_after = stale_after
        self.candles: dict[tuple[str, str, datetime], Candle] = {}
        self.last_sequence: dict[tuple[str, str], int] = {}

    def add(self, candle: Candle) -> FeedStatus:
        if not candle.finalized:
            raise ValueError("only finalized candles can enter the store")
        key = (candle.symbol, candle.interval, candle.close_time)
        self.candles[key] = candle
        stream = (candle.symbol, candle.interval)
        previous = self.last_sequence.get(stream)
        self.last_sequence[stream] = max(candle.sequence, previous or candle.sequence)
        missing = self._missing(stream)
        return FeedStatus(
            stale=False,
            gap_detected=bool(missing),
            blocks_entries=bool(missing),
            expected_sequence=(previous + 1) if previous is not None else None,
            missing_sequences=missing,
        )

    def status(self, symbol: str, interval: str, now: datetime | None = None) -> FeedStatus:
        now = now or datetime.now(timezone.utc)
        candles = [c for c in self.candles.values() if c.symbol == symbol and c.interval == interval]
        if not candles:
            return FeedStatus(stale=True, gap_detected=False, blocks_entries=True)
        latest = max(candles, key=lambda c: c.close_time)
        stale = now - latest.close_time > self.stale_after
        missing = self._missing((symbol, interval))
        return FeedStatus(stale=stale, gap_detected=bool(missing), blocks_entries=stale or bool(missing), missing_sequences=missing)

    def _missing(self, stream: tuple[str, str]) -> list[int]:
        sequences = sorted(c.sequence for c in self.candles.values() if (c.symbol, c.interval) == stream)
        if len(sequences) < 2:
            return []
        return [value for value in range(sequences[0], sequences[-1]) if value not in sequences]

