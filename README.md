# Jev Trading Bot

Phase 2 provides the Phase 1 foundation plus finalized market candles, Binance WebSocket/REST normalization, sequence-gap detection, and stale-feed status. The API refuses to start unless `PAPER_ONLY=true`; no order or live-execution route exists.

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
- Market status: `http://localhost:8000/market/status?symbol=BTCUSDT&interval=15m`

## Test

```powershell
cd api
python -m pytest
```

