import json
from pathlib import Path

from .contracts import ReplayRecord


def load_fixture(path: str | Path) -> ReplayRecord:
    return ReplayRecord.model_validate_json(Path(path).read_text(encoding="utf-8"))


def dump_fixture(record: ReplayRecord, path: str | Path) -> None:
    Path(path).write_text(record.model_dump_json(indent=2), encoding="utf-8")

