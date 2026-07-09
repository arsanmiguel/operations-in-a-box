# Secure Monitoring Stack

Enterprise-style monitoring solution with Prometheus, Grafana, and secure API.

## Quick Start

```bash
./install.sh
```

## What install does

1. Runs `scripts/bootstrap-env.sh` to create `.env` with random credentials (if missing or still using `change-me` placeholders)
2. Creates local `data/` directories for Prometheus and Grafana persistence
3. Builds and starts containers via Docker Compose
4. Waits for Prometheus, Grafana, and the API to pass health checks
5. Pushes an `install_heartbeat` sample metric so the default dashboard has data

## Services

| Service | URL | Notes |
|---------|-----|-------|
| Grafana | http://localhost:3000 | Login: `admin` + `GRAFANA_ADMIN_PASSWORD` from `.env` |
| Prometheus | http://localhost:9090 | Bound to localhost only |
| Metrics API | http://localhost:8080 | Requires `X-API-Key` header |

Default home dashboard: **Operations in a Box - Overview** (under folder *Operations in a Box*).

## Why credentials live in `.env`

Docker Compose reads secrets from a **local `.env` file**, not from files in git:

- **Grafana admin password and secret key** — unique per deployment; never shared in the repo
- **API key** — required for authenticated metric ingestion; the API refuses to start without `API_KEY` set

`.env.template` shows required variable names. Copy it to `.env` only if you need to set values manually; otherwise `install.sh` generates them for you.

Files that must stay local (gitignored):

- `.env` — deployment secrets
- `data/` — Prometheus TSDB and Grafana SQLite state
- `installation_report_*.json` — legacy install artifacts that may contain credentials

## Provisioned Grafana assets

Grafana dashboards and datasources ship under `grafana/provisioning/`:

- `datasources/prometheus.yml` — Prometheus at `http://prometheus:9090`
- `dashboards/default/monitoring-overview.json` — starter dashboard (targets up, API health, install heartbeat)

These load automatically on container start. Edit JSON files to change the default dashboard; use `AWS_MSP_DASHBOARD_WALKTHROUGH.md` in the parent directory for custom panels.

## Management

```bash
./install.sh               # First install (or re-run after pulling updates)
./start.sh                 # Start only (runs bootstrap-env if needed)
docker compose down        # Stop
docker compose logs -f     # View logs
```

## Security Features

- API key authentication (constant-time comparison)
- Non-root containers
- Read-only root filesystems where supported
- Security headers on API responses
- Input validation and rate limiting
- Localhost-only service bindings
