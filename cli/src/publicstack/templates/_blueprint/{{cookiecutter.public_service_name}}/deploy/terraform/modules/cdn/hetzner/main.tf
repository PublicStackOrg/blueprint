# {{ cookiecutter.public_service_name }} — cdn on hetzner (STUB).
#
# Not implemented in blueprint v0.4.0. The README.md documents the
# expected output contract. PRs welcome.

terraform {
  required_version = ">= 1.6"
}

resource "terraform_data" "not_implemented" {
  lifecycle {
    precondition {
      condition     = false
      error_message = "modules/cdn/hetzner/ is a stub in blueprint v0.4.0. See README.md for the output contract; PRs welcome."
    }
  }
}
