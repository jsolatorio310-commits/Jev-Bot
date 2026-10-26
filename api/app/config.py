import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    paper_only: bool
    postgres_dsn: str
    typesafe_api_key: str


def load_settings() -> Settings:
    paper_only = os.getenv("PAPER_ONLY", "true").lower() == "true"
    if not paper_only:
        raise RuntimeError("PAPER_ONLY must remain true in Phase 0")
    return Settings(
        paper_only=True,
        postgres_dsn=os.getenv("POSTGRES_DSN", "postgresql://trader:trader@localhost:5432/trading"),
        typesafe_api_key=os.getenv("TYPESAFE_API_KEY", ""),
    )

