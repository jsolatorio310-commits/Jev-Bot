from datetime import datetime, timedelta, timezone
from typing import Literal

from pydantic import BaseModel, Field


class Bar(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float


class RiskLimits(BaseModel):
    equity: float = Field(gt=0)
    risk_fraction: float = Field(default=0.01, gt=0, le=1)
    max_exposure_fraction: float = Field(default=0.25, gt=0, le=1)
    fee_fraction: float = Field(default=0.001, ge=0, le=1)


class Position(BaseModel):
    entry: float = Field(gt=0)
    quantity: float = Field(gt=0)
    stop: float = Field(gt=0)
    target: float = Field(gt=0)
    opened_at: datetime


class TradePlan(BaseModel):
    action: Literal["BUY", "SELL", "HOLD"]
    entry: float | None = None
    stop: float | None = None
    target: float | None = None
    quantity: float = 0
    expiry: datetime | None = None
    reasons: list[str] = Field(default_factory=list)


def ema(values: list[float], period: int) -> float | None:
    if len(values) < period:
        return None
    result = sum(values[:period]) / period
    multiplier = 2 / (period + 1)
    for value in values[period:]:
        result = (value - result) * multiplier + result
    return result


def atr(bars: list[Bar], period: int = 14) -> float | None:
    if len(bars) < period + 1:
        return None
    true_ranges = []
    for previous, current in zip(bars, bars[1:]):
        true_ranges.append(max(current.high - current.low, abs(current.high - previous.close), abs(current.low - previous.close)))
    return sum(true_ranges[-period:]) / period


def evaluate(
    intraday: list[Bar],
    hourly: list[Bar],
    limits: RiskLimits,
    position: Position | None = None,
    now: datetime | None = None,
) -> TradePlan:
    if not intraday or not hourly:
        return TradePlan(action="HOLD", reasons=["missing history"])
    current = intraday[-1]
    now = now or current.timestamp

    if position:
        if current.low <= position.stop:
            return TradePlan(action="SELL", entry=position.entry, stop=position.stop, target=position.target, quantity=position.quantity, reasons=["stop hit"])
        if current.high >= position.target:
            return TradePlan(action="SELL", entry=position.entry, stop=position.stop, target=position.target, quantity=position.quantity, reasons=["target hit"])
        if now >= position.opened_at + timedelta(hours=4):
            return TradePlan(action="SELL", entry=position.entry, stop=position.stop, target=position.target, quantity=position.quantity, reasons=["expiry reached"])
        return TradePlan(action="HOLD", reasons=["position open"])

    hourly_closes = [bar.close for bar in hourly]
    intraday_closes = [bar.close for bar in intraday]
    trend_fast = ema(hourly_closes, 50)
    trend_slow = ema(hourly_closes, 200)
    pullback = ema(intraday_closes[:-1], 20)
    reclaim = ema(intraday_closes, 20)
    current_atr = atr(intraday)
    if None in (trend_fast, trend_slow, pullback, reclaim, current_atr):
        return TradePlan(action="HOLD", reasons=["insufficient history"])
    if trend_fast <= trend_slow:
        return TradePlan(action="HOLD", reasons=["hourly trend filter failed"])
    if not (intraday[-2].low <= pullback and intraday[-2].close <= pullback < current.close):
        return TradePlan(action="HOLD", reasons=["EMA20 pullback/reclaim not present"])

    entry = current.close
    stop = entry - 1.5 * current_atr
    target = entry + 2 * (entry - stop)
    risk_per_unit = entry - stop
    quantity = min(
        limits.equity * limits.risk_fraction / risk_per_unit,
        limits.equity * limits.max_exposure_fraction / entry,
    )
    if quantity <= 0 or entry * quantity * (1 + limits.fee_fraction) > limits.equity * limits.max_exposure_fraction:
        return TradePlan(action="HOLD", reasons=["risk limit failed"])
    return TradePlan(
        action="BUY",
        entry=entry,
        stop=stop,
        target=target,
        quantity=quantity,
        expiry=current.timestamp + timedelta(hours=4),
        reasons=["hourly bullish trend", "EMA20 reclaim", "ATR14 stop", "2R target"],
    )

