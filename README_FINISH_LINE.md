# Finish-line package — digital-boxing-backend

Drop-in code to **replace / merge** into [trevsta00777-crypto/digital-boxing-backend](https://github.com/trevsta00777-crypto/digital-boxing-backend).

The public tree today is thin (`app/main.py` imports `app.auth.routes` which is missing). Docs/Docker claim “done”; this package supplies the missing working API.

## What this package adds

| Area | Contents |
|------|----------|
| App | `config`, `database`, `models` (incl. **Payment**), schemas, JWT auth, fighters/matches/events/training, Stripe Checkout + webhook, health |
| Security | CORS from env (no `*` in prod), rate-limit middleware, security headers |
| DB | Alembic `001_initial` migration |
| Ops | `scripts/backup_postgres.sh`, `restore_postgres.sh`, `docs/TLS_AND_DEPLOY.md` |
| Hygiene | `.gitignore` (ignores `.env*`), `.env.example` placeholders only |
| Tests | SQLite + mocked Stripe (`tests/`) |

## Manual merge / PR (no push from this agent)

1. Clone your repo locally (on your machine):
   ```bash
   git clone https://github.com/trevsta00777-crypto/digital-boxing-backend.git
   cd digital-boxing-backend
   git checkout -b finish-line/api-payments-security
   ```
2. Unzip this package and copy files over the repo root (review diffs):
   ```bash
   unzip boxing-finish-line.zip -d /tmp/boxing-finish-line
   # Copy app/, alembic/, scripts/, docs/, tests/, plus root files
   rsync -av --exclude ISSUES_CREATED.md --exclude README_FINISH_LINE.md \
     /tmp/boxing-finish-line/ ./
   ```
3. **Rotate secrets** if `.env` / `.env.development` / `.env.production` were ever committed. Remove them from git history if needed (`git filter-repo` / BFG). Keep only `.env.example`.
4. Install & verify:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env   # edit placeholders
   export DATABASE_URL=sqlite:///./dev.db   # quick local
   alembic upgrade head   # needs Postgres URL for real migrate
   pytest tests/ -v
   uvicorn app.main:app --reload
   ```
5. Commit and open a PR on GitHub (UI or `gh pr create`).
6. Follow `docs/TLS_AND_DEPLOY.md` for Railway/Fly/Render/AWS + Stripe Dashboard webhook URL.

## Replace vs keep

- **Replace** the thin `app/main.py` and missing modules with this `app/` tree.
- **Keep / adapt** existing `Dockerfile`, `docker-compose*.yml`, `k8s/` if you still want them — but prefer building from this real source tree instead of Dockerfile heredocs that invent files at image build time.
- Update root `README.md` when you merge (aspirational “everything done” claims should match reality).

## API surface (quick)

- `POST /auth/register` `POST /auth/login` `GET /auth/me`
- `CRUD /fighters` `/events` `/matches` `/training`
- `POST /payments/checkout` — Stripe Checkout for event tickets  
- `POST /payments/subscription/checkout` — light subscription stub  
- `POST /payments/webhook` — Stripe signature verify  
- `GET /payments/me` `GET /health`

## Tracking issues

See `ISSUES_CREATED.md` for GitHub issue URLs created for this workstream.
