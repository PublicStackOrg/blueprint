# `modules/cdn/aws/`

CloudFront distribution with two origins:

- **ALB origin** — the api service. Path-routes `/api/*`, `/v1/*`,
  `/health`, `/version` here. Cache-disabled (api responses aren't
  cacheable by default; tune per-route as needed).
- **S3 origin** — Flutter web builds (resident, staff, kiosk) uploaded
  by CI to a static-hosting S3 bucket. Default behavior, cached. SPA
  fallback rewrites 404 to `/index.html`.

The ALB origin is reached via Origin Access Control; the S3 origin
uses a separate OAC so the bucket can stay private.

## Cert region

ACM certs for CloudFront **must live in `us-east-1`**. The environment
spawns a separate `aws.us_east_1` provider alias and passes the cert
ARN in. The rest of the infra can live in any region.

## Inputs

| Variable | Required | Notes |
|---|---|---|
| `name_prefix` | yes | |
| `alb_dns_name` | yes | from `modules/compute/aws/` `service_endpoint` |
| `s3_static_origin_domain` | yes | static-hosting bucket regional domain |
| `cloudfront_certificate_arn` | yes | **must be in us-east-1** |
| `aliases` | no | `["parking.example.org"]` |
| `price_class` | no | `PriceClass_100` (US/CA/EU) by default |

## Outputs

| Output | Type |
|---|---|
| `distribution_domain_name` | string (the d12345.cloudfront.net) |
| `distribution_id` | string |
| `origin_endpoint` | string (alb_dns_name passthrough) |
| `hosted_zone_id` | string (Route 53 alias) |

## Cost

CloudFront pricing is per-request + per-byte; the floor is near-zero
at small-city scale. Typical small-city PS: <$5/mo unless content is
heavily downloaded.
