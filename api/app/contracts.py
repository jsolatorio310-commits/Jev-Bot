from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Snapshot(BaseModel):
    snapshot_id: UUID = Field(default_factory=uuid4)
    symbol: str
    interval: str = "15m"
    close_time: str
    configuration_hash: str


class Decision(BaseModel):
    decision_id: UUID = Field(default_factory=uuid4)
    snapshot_id: UUID
    action: Literal["BUY", "SELL", "HOLD"]
    status: Literal["approved", "blocked", "unresolved"]
    blockers: list[str] = Field(default_factory=list)
    config_version: str


class LedgerEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_key: str
    event_type: Literal["balance", "position", "order", "fill"]
    payload: dict


class ReplayRecord(BaseModel):
    snapshot: Snapshot
    decision: Decision
    events: list[LedgerEvent] = Field(default_factory=list)

