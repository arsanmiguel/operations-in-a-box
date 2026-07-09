# Security design notes — Operations in a Box

Intentional security choices for the **reference monitoring stack** (local Docker lab starting point).  
These are **by design** for localhost-first deployment — adjust deliberately if you change the architecture.

**Related:** [README](../README.md) · [SECURITY_GUIDE.md](SECURITY_GUIDE.md) · [customer-monitoring-stack/README.md](customer-monitoring-stack/README.md)

---

## What this stack includes

A Docker Compose monitoring lab (Prometheus, Grafana, Pushgateway, metrics API). It is not a multi-tenant SaaS. The base installer starts the **core stack only**; optional integration templates under `customer-monitoring-stack/plugins/` are filled in locally.

**Validate a local install:**

```bash
cd observability-stack/customer-monitoring-stack
./scripts/bootstrap-env.sh    # creates .env (gitignored) if missing
python3 ../security_validator.py --install-dir .
```

Do not commit `customer-monitoring-stack/.env`. Tear down with `uninstall.sh` when finished.

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

## Plugin templates (optional)

**Design:** `customer-monitoring-stack/plugins/*` are **49 optional integration templates** (third-party APIs, extra containers). They are not started by the base installer.

Customers copy templates, add credentials locally, and run plugin install commands as needed. Plugin `*-api-keys.json` files in git are **metadata stubs** (name/version/enabled), not live secrets.

---

## Rate limits and API key auth

**Design:** Metrics API uses `X-API-Key` from `.env`, constant-time compare, Flask-Limiter defaults documented in `SECURITY_GUIDE.md`.

**Why:** Suitable for lab and single-tenant deployments; production may need OAuth/SAML (see `saml-auth` plugin template).

---

## What we hardened (not exceptions)

Core stack already implements:

- Non-root container users
- Read-only rootfs, `cap_drop: ALL`, `no-new-privileges`
- Cryptographic `.env` generation (`bootstrap-env.sh`)
- Security headers, input validation, rate limiting on API

See `security_validator.py` for the checklist.
