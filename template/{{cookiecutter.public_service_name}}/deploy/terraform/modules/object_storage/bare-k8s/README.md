# `modules/object_storage/bare-k8s/`

MinIO (S3-compatible) on Kubernetes via the Bitnami helm chart. Same
outputs as `modules/object_storage/aws/` (with sensible substitutions
for fields that don't apply: bucket_arn becomes a `minio://` URL,
region is hardcoded `us-east-1`).

Inputs match the AWS variant's contract. Storage size is configurable
via `storage_gb`. Credentials auto-generated and stored in a
kubernetes_secret named `<bucket>-minio`.

The `document_storage` Grid adapter targets MinIO via S3-compatible
endpoint:

```yaml
DOCUMENT_STORAGE_BACKEND=s3
DOCUMENT_STORAGE_S3_ENDPOINT=http://<bucket>.<ns>.svc.cluster.local:9000
DOCUMENT_STORAGE_S3_BUCKET=<bucket>
# AWS-style creds from the k8s_secret
```
