import json
import sqlite3
from pathlib import Path

from .contracts import LedgerEvent


SCHEMA = """
CREATE TABLE IF NOT EXISTS ledger_events (
    event_id TEXT PRIMARY KEY,
    event_key TEXT NOT NULL UNIQUE,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS balances (
    asset TEXT PRIMARY KEY,
    amount REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS positions (
    symbol TEXT PRIMARY KEY,
    quantity REAL NOT NULL,
    average_price REAL NOT NULL
);
"""


class Ledger:
    def __init__(self, path: str | Path = ":memory:"):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)

    def append(self, event: LedgerEvent) -> LedgerEvent:
        self.db.execute(
            "INSERT INTO ledger_events (event_id, event_key, event_type, payload) VALUES (?, ?, ?, ?)",
            (str(event.event_id), event.event_key, event.event_type, json.dumps(event.payload, sort_keys=True)),
        )
        self.db.commit()
        return event

    def events(self) -> list[LedgerEvent]:
        rows = self.db.execute("SELECT * FROM ledger_events ORDER BY created_at, rowid").fetchall()
        return [LedgerEvent(event_id=row["event_id"], event_key=row["event_key"], event_type=row["event_type"], payload=json.loads(row["payload"])) for row in rows]

    def rebuild(self) -> dict:
        balances: dict[str, float] = {}
        positions: dict[str, dict[str, float]] = {}
        for event in self.events():
            if event.event_type == "balance":
                asset = event.payload["asset"]
                balances[asset] = balances.get(asset, 0) + event.payload["delta"]
            elif event.event_type == "position":
                symbol = event.payload["symbol"]
                position = positions.setdefault(symbol, {"quantity": 0, "average_price": 0})
                position["quantity"] += event.payload["quantity_delta"]
                position["average_price"] = event.payload.get("average_price", position["average_price"])
        return {"balances": balances, "positions": positions}

