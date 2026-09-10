# TLS, Deploy Options & Stripe Dashboard (Human Steps)

Deploy target is undecided. Pick one platform below; TLS terminates at the reverse proxy / platform edge — the FastAPI app listens on HTTP inside the private network.

## Shared prerequisites

1. Copy `.env.example` → `.env` (or platform secrets). **Never commit `.env*`.**
2. Generate secrets:
   ```bash
   openssl rand -hex 32   # SECRET_KEY
   ```
3. Set `CORS_ORIGINS` to your real front-end origins (comma-separated). Do **not** use `*` in production.
4. Run migrations against Postgres:
   ```bash
   alembic upgrade head
   ```
5. Schedule `scripts/backup_postgres.sh` (cron / platform job) and store dumps off-box.

## TLS at the reverse proxy

- App binds `0.0.0.0:8000` over HTTP.
- Proxy (Caddy / nginx / Traefik / cloud LB) terminates TLS and forwards to the app.
- Require HTTPS redirect; enable HSTS at the edge (app also sends HSTS when `ENV=production`).
- Webhook endpoint must be publicly reachable over HTTPS:
  `https://<your-domain>/payments/webhook`

Example nginx snippet (illustrative):

```nginx
server {
  listen 443 ssl http2;
  server_name api.example.com;
  # ssl_certificate / ssl_certificate_key managed by certbot or ACM
  location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
```

## Platform notes

### Railway
- New Project → Deploy from GitHub repo.
- Add Postgres plugin; map `DATABASE_URL` (or discrete `POSTGRES_*`).
- Set env vars from `.env.example`.
- Public domain + automatic TLS provided by Railway.
- Health check path: `/health`.

### Fly.io
- `fly launch` / Dockerfile; attach Fly Postgres or external DB.
- `fly secrets set SECRET_KEY=... STRIPE_SECRET_KEY=...`
- TLS via Fly proxy on `.fly.dev` or custom domain.

### Render
- Web Service from Dockerfile or `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- Managed Postgres; set env in dashboard.
- Automatic TLS on `onrender.com` / custom domain.

### AWS (ECS/Fargate or Elastic Beanstalk + RDS)
- Put ALB / CloudFront in front with ACM certificate.
- RDS Postgres; store secrets in Secrets Manager / SSM.
- Security groups: only ALB → task:8000; no public DB.
- Optional: API Gateway HTTP API as edge.

## Stripe Dashboard (human steps)

1. Create a Stripe account; use **Test mode** until go-live.
2. Developers → API keys → copy **Secret** + **Publishable** into env (`STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`).
3. Developers → Webhooks → Add endpoint:
   - URL: `https://<your-domain>/payments/webhook`
   - Events: `checkout.session.completed`, `checkout.session.expired`, `payment_intent.payment_failed`
4. Copy the webhook **Signing secret** → `STRIPE_WEBHOOK_SECRET`.
5. Set `STRIPE_SUCCESS_URL` / `STRIPE_CANCEL_URL` to your front-end pages.
6. (Optional subscriptions) Products → create Price → set `STRIPE_SUBSCRIPTION_PRICE_ID`.
7. Local testing: `stripe listen --forward-to localhost:8000/payments/webhook`.

## Post-deploy checklist

- [ ] `/health` returns `{"status":"ok"}`
- [ ] Register + login works; JWT on `/auth/me`
- [ ] CORS rejects unknown origins
- [ ] Stripe test Checkout completes; Payment row → `completed` via webhook
- [ ] Backup script produces a `.sql.gz` + `.sha256`
- [ ] Confirm `.env*` are gitignored and rotated if previously committed
