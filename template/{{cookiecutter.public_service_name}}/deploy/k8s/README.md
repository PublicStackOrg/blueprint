# Helm chart deploy

Cloud-agnostic K8s deployment of **{{ cookiecutter.public_service_name }}**.
Installable on EKS, GKE, AKS, kind — anywhere there's a Kubernetes
cluster.

## Quickstart on `kind` (local)

```bash
kind create cluster --name {{ cookiecutter.public_service_slug }}
helm dep update ./deploy/k8s

helm install {{ cookiecutter.public_service_slug }} ./deploy/k8s \
  --set publicHostname={{ cookiecutter.public_service_slug }}.local \
  --set postgresql.auth.password=$(openssl rand -hex 32) \
  --set redis.auth.password=$(openssl rand -hex 32)

kubectl rollout status deploy/{{ cookiecutter.public_service_slug }}-api
kubectl port-forward svc/{{ cookiecutter.public_service_slug }}-api 8000:8000
curl http://localhost:8000/health
```

## Production install (EKS/GKE/AKS)

```bash
helm dep update ./deploy/k8s
helm install {{ cookiecutter.public_service_slug }} ./deploy/k8s \
  --namespace {{ cookiecutter.public_service_slug }} \
  --create-namespace \
  -f values-prod.yaml \
  --set postgresql.auth.password=$(openssl rand -hex 32) \
  --set redis.auth.password=$(openssl rand -hex 32)
```

`values-prod.yaml` overrides:

```yaml
publicHostname: parking.example.org

api:
  replicaCount: 3
  autoscaling:
    enabled: true

ingress:
  className: alb               # or nginx, gce — match your cluster
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
```

## Bring-your-own Postgres / Redis

Disable the Bitnami subcharts and point at managed services (RDS,
ElastiCache, Cloud SQL, etc.):

```yaml
postgresql:
  enabled: false
externalPostgres:
  enabled: true
  url: postgresql+asyncpg://...
  secretName: external-pg

redis:
  enabled: false
externalRedis:
  enabled: true
  url: redis://...
  secretName: external-redis
```

## Migrator runs as a Helm hook

The migrator `Job` carries `helm.sh/hook: pre-install,pre-upgrade` so
it runs before each install/upgrade and the api/worker rollouts wait
on its completion. No service mesh / orchestration required.

## Compliance suite from inside the cluster

The PublicStack compliance suite runs out-of-cluster (it inspects the
PS repo's source tree). For runtime monitoring, scrape `/metrics`
through your Prometheus stack — the FastAPI service exposes it at
`<api-svc>:8000/metrics` (basic-auth gated; see Caddyfile pattern in
deploy/compose/ for the equivalent).
