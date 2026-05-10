# Licensing

PublicStack is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. See [LICENSE](./LICENSE) for the full text.

This is the default license for **all repositories** in the PublicStack organization.

## Why AGPL-3.0

PublicStack exists to keep civic infrastructure in the commons — out of the hands of vendors who extract recurring revenue from cities and residents. The license has to enforce that intent, not just hope for it.

### Permissive licenses don't work for this project

A permissive license (MIT, Apache, BSD) lets anyone take the code, build proprietary features on top, and sell it back to cities as closed software. That is exactly the dynamic PublicStack is built to break. A MIT-licensed parking module would last about a quarter before a vendor forked it, added a dashboard, and started selling it to municipalities under a per-transaction contract — with no obligation to share improvements back.

### Plain GPL has the SaaS loophole

GPL-2 and GPL-3 only trigger their share-alike requirement when software is **distributed**. Modern civic software is delivered as a hosted service — a city points its DNS at someone's server. Nothing is being distributed in the legal sense, so plain GPL doesn't apply. A vendor could host a modified PublicStack module and never share their changes.

### AGPL closes that loophole

AGPL-3.0 extends the share-alike requirement to **network use**: if you let users interact with modified PublicStack code over a network, you have to make the source available to those users. This is the right shape for civic software. It says:

- **Self-host PublicStack as a city.** Free, no obligations beyond providing source to your residents on request (which you should do anyway as a public institution).
- **Run a managed hosting service for cities.** Allowed, but your modifications stay open. Competing service providers can't lock improvements behind a paywall.
- **Build a proprietary fork and sell it as a closed SaaS.** Not allowed. The license forbids it.

This is the same license used by [Mastodon](https://github.com/mastodon/mastodon), [Grafana](https://github.com/grafana/grafana), [Nextcloud](https://github.com/nextcloud/server), and [Bitwarden](https://github.com/bitwarden/server) — all projects that explicitly wanted to prevent SaaS extraction.

## What this means in practice

**For cities:** You can run, modify, and self-host any PublicStack module forever, without paying anyone. If you make changes you think are useful, contributing them back is encouraged but only required if you let other organizations use your modified version over the network.

**For developers and contractors building for cities:** You can absolutely use PublicStack code in work you do for a municipality. Your modifications need to be made available to the users of the system. In a civic context, that's almost always the right answer anyway.

**For commercial vendors:** You can offer hosting, support, customization, and integration services around PublicStack. You can charge for any of it. You cannot take the code, build proprietary features behind closed doors, and run it as a SaaS without sharing your modifications with users.

**For PublicStack's own managed hosting service:** Same rules apply. The hosted version of PublicStack runs on the same code that's in this organization, and any improvements made for hosted customers flow back into the public repos.

## Module-by-module

This file documents the org-wide default. Individual repos within the PublicStack organization may carry their own `LICENSE` and `LICENSING.md` files reflecting the same default. If a specific module ever needs a different license — for example, a client library intended to be embedded in third-party apps might use LGPL or Apache 2.0 to allow that — that exception will be documented in that module's own README.

## Contributor License Agreement

PublicStack does not require a CLA. Contributions are accepted under the inbound=outbound principle: when you contribute code, you're licensing your contribution under the same terms as the project itself. If that ever changes — for example, to enable dual-licensing for specific modules — it will be announced and discussed publicly first.

## Disclaimer

This document explains why PublicStack chose AGPL-3.0 and how the license is intended to apply. It is not legal advice. The binding terms are in [LICENSE](./LICENSE), and questions about specific obligations should go to a lawyer familiar with open-source licensing.
