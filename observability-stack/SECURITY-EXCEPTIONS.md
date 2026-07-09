# Security exceptions — Operations in a Box

Intentional security choices for the **reference monitoring stack** (local Docker lab starting point).  
These are **by design** for localhost-first deployment — do not “fix” without an explicit architecture change.

**Related:** [README](../README.md) · [SECURITY_GUIDE.md](SECURITY_GUIDE.md) · [customer-monitoring-stack/README.md](customer-monitoring-stack/README.md)

---

## CSE / security scan handoff

**What this is:** A Docker Compose monitoring lab (Prometheus, Grafana, Pushgateway, metrics API). Not a multi-tenant SaaS. Core scan scope is the **base stack**, not all 49 optional plugin templates.

**Templates / paths in scope:**

| Path | Role |
|------|------|
| `customer-monitoring-stack/docker-compose.yml` | **Core deploy** — what `install.sh` runs |
| `customer-monitoring-stack/api/` | Metrics API (Flask) + Dockerfile |
| `*.py`, `*.sh` (this directory) | Installers and validators |

**Run automated scans (Docker required; Colima on macOS):**

```bash
colima start   # if needed
cd observability-stack
./security-scan.sh
```

Optional full plugin template scan:

```bash
SCAN_PLUGINS=1 ./security-scan.sh
```

Reports default to `/tmp/operations-in-a-box-security-scan/` (`latest-trivy-*.txt`, `latest-gitleaks.txt`, `latest-security-validator.txt`, optional hadolint/shellcheck).

**Runtime validation (included in scan script):**

```bash
cd customer-monitoring-stack
./scripts/bootstrap-env.sh    # creates .env (gitignored) if missing
python3 ../security_validator.py --install-dir .
```

Expect **9/9** checks when `.env` is generated and core files are unchanged.

**Before filing findings, read:**

- This document (localhost binding, Grafana HTTP cookies, plugin scope)
- [`.gitleaks.toml`](../.gitleaks.toml) — documentation placeholder allowlist

**Operational note:** Do not commit `customer-monitoring-stack/.env`. Tear down with `uninstall.sh` when done.

---

## Localhost-only service binding

**Design:** Prometheus, Grafana, Pushgateway, and the metrics API bind to **`127.0.0.1`** only in `docker-compose.yml`.

**Why:** Default install is a **single-operator lab** on a laptop or bastion. Remote access should go through SSH tunnel or an explicit front proxy you add for production.

**Production path:** Put TLS termination and auth in front (ALB, reverse proxy, SAML plugin) before exposing beyond localhost.

---

## Grafana HTTP cookie settings (local install)

**Design:** In core `docker-compose.yml`:

- `GF_SECURITY_COOKIE_SECURE=false`
- `GF_SECURITY_STRICT_TRANSPORT_SECURITY=false`
- `GF_SERVER_ROOT_URL=http://localhost:3000`

**Why:** Install guide uses **plain HTTP on localhost**. Enabling secure cookies / HSTS without TLS breaks login on first-run.

**Production path:** Terminate HTTPS at a proxy and set `GF_SERVER_ROOT_URL`, `GF_SECURITY_COOKIE_SECURE=true`, and HSTS appropriately.

---

## Plugin templates (out of core CSE scope)

**Design:** `customer-monitoring-stack/plugins/*` are **49 optional integration templates** (third-party APIs, extra containers). They are not started by the base installer.

**CSE default:** `./security-scan.sh` scans **core stack only**. Set `SCAN_PLUGINS=1` to include plugin trees (expect third-party config noise; customers fill credentials locally).

Plugin `*-api-keys.json` files in git are **metadata stubs** (name/version/enabled), not live secrets.

---

## Rate limits and API key auth

**Design:** Metrics API uses `X-API-Key` from `.env`, constant-time compare, Flask-Limiter defaults documented in `SECURITY_GUIDE.md`.

**Why:** Suitable for lab and single-tenant deployment handoff; production may need OAuth/SAML (see `saml-auth` plugin template).

---

## What we hardened (not exceptions)

Core stack already implements:

- Non-root container users
- Read-only rootfs, `cap_drop: ALL`, `no-new-privileges`
- Cryptographic `.env` generation (`bootstrap-env.sh`)
- Security headers, input validation, rate limiting on API

See `security_validator.py` for the checklist.
