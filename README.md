# Jev Trading Bot

Phase 0 provides the local foundation only: Docker Compose, a FastAPI health/control service, a React shell, and PostgreSQL. The API refuses to start unless `PAPER_ONLY=true`; no order or live-execution route exists.

## Run

```powershell
Copy-Item .env.example .env
docker compose up --build
```

- API health: `http://localhost:8000/health`
- Web shell: `http://localhost:3000`
- PostgreSQL: `localhost:5432`, database `trading`, user/password `trader`

## Test

```powershell
cd api
python -m pytest
```

