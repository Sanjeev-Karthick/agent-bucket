# Contributing

Welcome! V0.1 is a developer preview. Small, focused contributions are especially useful.

1. Read [architecture](docs/architecture.md) and the [roadmap](ROADMAP.md).
2. Open an issue for significant design changes. For a small fix, send a PR directly.
3. Use Python 3.12, Node 22+, uv and npm. Run `make setup` and `make check`.
4. Add behavior tests when changing ingestion, retrieval, persistence or auth.
5. Describe the user-visible change, checks run and limitations in the PR template.

Run `docker compose -f compose.minio.yaml up -d` and `make integration` for S3 changes.
Tests use synthetic data and hash embeddings; no model downloads are required.
Never commit credentials, real customer documents, caches or generated indexes.

Use Ruff for Python formatting and lint, mypy for backend types, and ESLint/TypeScript
for the UI. Keep adapters independent of HTTP handlers. Do not add distributed
infrastructure to the V0.1 deployment without discussing an ADR first.

Commits should explain intent. We use Apache-2.0; by submitting a contribution you
agree that your contribution is licensed under the repository license. No CLA is
currently required. Maintainers review changes as time allows; there is no response SLA.

See [starter issues](docs/good-first-issues.md) for bounded tasks.
