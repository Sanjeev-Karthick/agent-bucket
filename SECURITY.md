# Security policy

## Supported versions

The default branch is a developer preview. No stable release or security support
window has been declared. Fixes land on the default branch until a release policy exists.

## Reporting a vulnerability

Use GitHub's **Security → Report a vulnerability** for this repository:
https://github.com/Sanjeev-Karthick/agent-bucket/security/advisories/new

If that option is unavailable, ask the maintainer for a private channel without
including exploit details in a public issue. Include affected revision, reproduction,
impact and a suggested fix if available. We do not promise an incident-response SLA.

## Deployment boundary

- V0.1 assumes one trusted operator and one authorized corpus. Every token holder
  can read all indexed text and trigger a sync. There are no per-user ACLs or tenants.
- Bind to loopback by default. Set a unique `AB_API_TOKEN` before using private data.
  Terminate TLS and enforce body-size/rate limits at your gateway for remote access.
- `/healthz`, `/docs`, `/openapi.json` and UI assets are public; `/v1/*` and `/mcp`
  require a bearer token. The UI holds its token only in memory.
- Use read-only ListBucket/GetObject credentials scoped to the configured prefix.
  Credentials stay in the boto3 credential chain, outside the control database.
- Parsed text and embeddings are local, sensitive copies of your objects. Protect
  and encrypt the host volume and backups. Deletions are logical; old Lance versions
  and backups may retain text until a separately designed retention policy removes it.
- Documents are untrusted input. Object byte limits do not bound PDF decompression,
  parser CPU or model memory. Use trusted corpora in this preview; parser sandboxing,
  execution deadlines and resource budgets are roadmap items.
- Retrieved content may contain prompt injections. Agents must treat it as data,
  preserve provenance and keep tool authorization separate from retrieved instructions.
- Model artifacts may be downloaded by FastEmbed/Docling. Review model licenses,
  supply chain and outbound network policy before handling restricted data.

MCP checks localhost Host/Origin values. Remote deployment needs an explicit reviewed
allowlist in `app.py`; do not disable DNS-rebinding protection as a workaround.
