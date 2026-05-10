# `modules/object_storage/aws/`

S3 bucket for the `document_storage` Grid service, configured the way
PublicStack expects: versioned, encrypted, public access blocked,
old-version lifecycle, optional CORS for browser uploads.

The per-PS Grid adapter (`libraries/grid_adapters/grid_adapters/
document_storage/`) targets the bucket via `DOCUMENT_STORAGE_BACKEND=s3`
+ `DOCUMENT_STORAGE_S3_BUCKET=<bucket_name>` env vars. The adapter is
the swap point — Terraform provisions, the adapter consumes.

## Inputs

| Variable | Required | Default | Notes |
|---|---|---|---|
| `bucket_name` | yes | — | globally unique; convention `<ps>-<env>-documents` |
| `noncurrent_version_expiration_days` | no | 30 | older versions get expired |
| `allowed_origins` | no | `[]` | empty = no CORS rule |
| `deletion_protection` | no | `false` | true → `terraform destroy` refuses |

## Outputs

| Output | Type |
|---|---|
| `bucket_name` | string |
| `bucket_arn` | string |
| `endpoint` | string (`<bucket>.s3.<region>.amazonaws.com`) |
| `region` | string |

## Cost

S3 charges for storage + requests, no compute floor. ~1 GB of
documents at ~$0.023/GB-month is negligible. The dev/staging dataset
typically costs <$1/mo.
