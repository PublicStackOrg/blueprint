# Single-VPS docker-compose deploy

The cheapest path to a running **{{ cookiecutter.public_service_name }}** —
one Linux VPS, public IP, 30 minutes from clone to live.

## Prerequisites

- Ubuntu 22.04+ VPS with at least 2 GB RAM (Hetzner CX21, DO basic-2gb,
  Vultr 2gb regular all qualify).
- A DNS A record pointing at the VPS — e.g. `parking.example.org → 1.2.3.4`.
  **Required before first boot** so Caddy can complete the Let's Encrypt
  HTTP-01 challenge.
- Docker Engine + Docker Compose v2 installed:

  ```bash
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker "$USER"
  newgrp docker
  ```

- Optional: `git`, `make`, your favorite text editor.

## Walkthrough

### 1. Clone the repo onto the VPS

```bash
ssh ubuntu@1.2.3.4
git clone https://github.com/{{ cookiecutter.github_org }}/{{ cookiecutter.public_service_name }}.git
cd {{ cookiecutter.public_service_name }}
```

### 2. Configure the env file

```bash
cp deploy/compose/.env.prod.example .env.prod
vi .env.prod
```

Required fields:

- `PUBLIC_HOSTNAME` — must match the DNS record.
- `IMAGE_TAG` — defaults to `latest`. Pin to a specific commit SHA
  (`git-abc1234`) for reproducible deploys.
- `POSTGRES_PASSWORD` and `REDIS_PASSWORD` — `openssl rand -hex 32` each.
- `METRICS_BASIC_AUTH` — generate via `caddy hash-password`, then format
  as `username $hashed_password`.

### 3. Build the Flutter web apps

The compose stack bind-mounts `apps/<x>/build/web/` into Caddy. Build
each app once (and again whenever you deploy a new version):

```bash
cd apps/resident && flutter build web --release && cd -
cd apps/staff && flutter build web --release && cd -
cd apps/kiosk && flutter build web --release && cd -
```

If you don't have Flutter on the VPS, build locally and `rsync` the
`build/web/` directories up.

### 4. Pull images + start the stack

```bash
docker compose -f deploy/compose/prod.yml --env-file .env.prod pull
docker compose -f deploy/compose/prod.yml --env-file .env.prod up -d
```

The `migrator` runs once and exits; `api` + `worker` start after it
completes. Caddy acquires a Let's Encrypt cert on first request.

### 5. Verify

```bash
curl -fsSL https://${PUBLIC_HOSTNAME}/health     # → {"status":"ok",...}
curl -fsSL https://${PUBLIC_HOSTNAME}/version    # → {"version":"0.0.1",...}
docker compose -f deploy/compose/prod.yml ps     # → all services healthy
```

Open `https://${PUBLIC_HOSTNAME}/` in a browser — the resident app
loads. `/staff` and `/kiosk` host the other Flutter web builds.

## Operations

### Updating to a new version

```bash
git pull
# rebuild Flutter web (step 3) if app code changed
docker compose -f deploy/compose/prod.yml --env-file .env.prod pull
docker compose -f deploy/compose/prod.yml --env-file .env.prod up -d
```

### Logs

```bash
docker compose -f deploy/compose/prod.yml logs -f caddy api worker
```

### Backups

The `postgres_data` volume is the durable state. Cron-style nightly
dump:

```bash
docker compose -f deploy/compose/prod.yml exec -T db \
  pg_dump -U {{ cookiecutter.python_package }} -F c {{ cookiecutter.python_package }} \
  > /var/backups/{{ cookiecutter.python_package }}-$(date +%F).pgdump
```

Wire that into a system cron and ship dumps off-VPS (e.g., to S3, B2,
or another box).

### Cert troubleshooting

Caddy's data volume (`caddy_data`) holds Let's Encrypt certs and
account state. If issuance fails on first boot:

```bash
docker compose -f deploy/compose/prod.yml logs caddy
```

Most common cause: DNS hadn't propagated yet. Wait a few minutes and
re-run `up -d`.

## Cost floor

A small-city Parking deploy fits comfortably on a 2-vCPU / 4 GB VPS.
See `blueprint/docs/cost-floor.md` for the design budget.

## When to step up

The single-VPS path runs out of headroom at:

- Sustained CPU > 60% across all services
- Active resident sessions > ~500 concurrent
- Postgres dataset > ~10 GB

At that point, look at `deploy/HOSTING.md` for the K8s + Terraform
on-ramps.
