# Jev Trading Bot

Phase 1 provides the local foundation plus versioned contracts, replay fixtures, an append-only ledger, idempotent event keys, and portfolio rebuilds. The API refuses to start unless `PAPER_ONLY=true`; no order or live-execution route exists.

## Run

```powershell
Copy-Item .env.example .env
docker compose up --build
```

- API health: `http://localhost:8000/health`
- Web shell: `http://localhost:3000`
- PostgreSQL: `localhost:5432`, database `trading`, user/password `trader`
- API OpenAPI: `http://localhost:8000/docs`
- Portfolio projection: `http://localhost:8000/ledger/portfolio`
- Checked-in JSON Schemas: `contracts/`

## Test

```powershell
cd api
python -m pytest
```

