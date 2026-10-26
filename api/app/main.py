from dataclasses import dataclass

from fastapi import FastAPI, HTTPException

from .config import load_settings

settings = load_settings()
app = FastAPI(title="Jev Trading Bot API", version="0.1.0")


@dataclass
class RuntimeState:
    emergency_stopped: bool = False


state = RuntimeState()


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


# Phase 0 intentionally exposes no order or execution routes.

