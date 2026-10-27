from dataclasses import dataclass

from fastapi import FastAPI, HTTPException

from .config import load_settings
from .contracts import LedgerEvent
from .ledger import Ledger
from .market import Candle, CandleStore
from .strategy import StrategyRequest, TradePlan, evaluate

settings = load_settings()
app = FastAPI(title="Jev Trading Bot API", version="0.1.0")


@dataclass
class RuntimeState:
    emergency_stopped: bool = False


state = RuntimeState()
ledger = Ledger()
market_store = CandleStore()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "paper_only": settings.paper_only,
        "emergency_stopped": state.emergency_stopped,
    }


@app.post("/controls/emergency-stop")
def emergency_stop() -> dict:
    state.emergency_stopped = True
    return {"emergency_stopped": True}


@app.post("/controls/resume")
def resume() -> dict:
    if state.emergency_stopped is False:
        raise HTTPException(status_code=409, detail="emergency stop is not active")
    state.emergency_stopped = False
    return {"emergency_stopped": False}


@app.post("/ledger/events", status_code=201)
def append_ledger_event(event: LedgerEvent) -> LedgerEvent:
    try:
        return ledger.append(event)
    except Exception as exc:
        raise HTTPException(status_code=409, detail="event_key already exists") from exc


@app.get("/ledger/portfolio")
def portfolio() -> dict:
    return ledger.rebuild()


@app.post("/market/candles", status_code=201)
def add_candle(candle: Candle) -> dict:
    try:
        status = market_store.add(candle)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"candle": candle, "feed_status": status}


@app.get("/market/status")
def market_status(symbol: str, interval: str = "15m") -> dict:
    return market_store.status(symbol, interval)


@app.post("/strategy/evaluate", response_model=TradePlan)
def evaluate_strategy(request: StrategyRequest) -> TradePlan:
    return evaluate(request.intraday, request.hourly, request.limits, request.position, request.now)


# Phase 0 intentionally exposes no order or execution routes.

