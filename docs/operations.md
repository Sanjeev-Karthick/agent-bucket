# Operations

## Configuration

Copy `.env.example` for the offline demo. `Settings` in `backend/agent_bucket/config.py`
is the authoritative list and validates limits. Environment variables override `.env`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `AB_SOURCE` | `demo` | `demo` directory or `s3` bucket |
| `AB_EMBEDDING_PROVIDER` | `fastembed` | `.env.example` explicitly uses `hash` |
| `AB_EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | FastEmbed model name |
| `AB_EMBEDDING_DIMENSIONS` | `384` | Must match the selected model |
| `AB_DATA_DIR` | `.data` | SQLite, LanceDB and model cache |
| `AB_CHUNK_CHARS` / `AB_CHUNK_OVERLAP` | `1600` / `160` | Character chunker |
| `AB_MAX_OBJECT_BYTES` / `AB_MAX_OBJECTS` | 20 MiB / 10,000 | Input and inventory limits |
| `AB_API_TOKEN` | demo token | Shared trusted-operator bearer token |

For S3, set `AB_SOURCE=s3`, `AB_S3_BUCKET` and optionally `AB_S3_ENDPOINT`,
`AB_S3_PREFIX`, `AB_S3_REGION`, `AB_S3_ADDRESSING_STYLE`. Omit the endpoint for AWS.
Boto3 uses its standard credential chain; prefer an IAM role with read-only permissions.

Compose sets `/data`, `/app/ui` and `/app/demo-data` inside the image. `.env` host
paths are deliberately not forwarded. Compose forwards AWS credential environment
variables; mount a credentials file explicitly if using a local AWS profile in Docker.
Do not use `localhost` for another container: use its service DNS name on a shared network.

## Real parsing and semantic retrieval

```sh
uv sync --frozen --extra dev --extra inference --extra parsing
```

Set `AB_EMBEDDING_PROVIDER=fastembed` and choose a fresh `AB_DATA_DIR`, then run
`make dev`. The first embedding/PDF parse may download model artifacts and take time.
Text and Markdown work without Docling. OCR is disabled in the starter. On Linux,
the lockfile sources PyTorch/torchvision from the official CPU wheel index to avoid
installing GPU runtimes in this single-node container.

## Backup and restore

Stop the service cleanly, copy the entire data volume (including SQLite WAL/SHM if
present and the complete Lance directory), then restart. Restore the entire copy
into a fresh directory with the same source/model settings. Verify status, run a sync
and perform a known query. Live filesystem copies are not a supported backup method.
Raw temporary parser files are removed after conversion; parsed text remains in the index.

## Troubleshooting

- 401: check the bearer token; the UI asks for the configured value.
- Empty results: enqueue sync and inspect `/v1/jobs`; sync is explicit, not automatic.
- Job failed: inspect the error class; confirm credentials, readable formats, optional
  packages, model download access and object limits. Errors are sanitized to avoid
  leaking credentials/content; diagnostics remain intentionally minimal in this starter.
- Identity mismatch: use a new data directory/volume and reindex.
- Process lock: stop the other instance; never run multiple workers on the same data.
- MCP 400/403: use `/mcp/`, the correct Accept header and a localhost Host/Origin.

Do not run `docker compose down -v` on data you need; it removes the index volume.
Public-host deployment needs a reviewed gateway and MCP host allowlist; see SECURITY.md.

## Toolchain dependencies

The UI overrides transitive `minimatch` to its patched 11.x line for
[GHSA-g3hv-75wg-m249](https://github.com/advisories/GHSA-g3hv-75wg-m249).
Revisit this override when ESLint/TypeScript tooling updates its own constraints.
Run the lint, type, test and build checks after updating either lockfile.
