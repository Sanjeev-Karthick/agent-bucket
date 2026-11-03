# Test plan

`make check` runs Python lint/format/type checks and unit/API tests, plus UI lint,
types, tests and build. The default suite uses synthetic text and hash embeddings.
It checks auth on both transports, MCP discovery/calls, search modes, incremental
sync/deletion, input limits, queue deduplication and restart recovery.

## MinIO integration

```sh
docker compose -f compose.minio.yaml up -d
make integration
make seed
```

Wait for MinIO to accept connections on localhost:9000 before the tests. The test
creates a uniquely named bucket, uploads synthetic text, syncs through the real S3
adapter, queries BM25 and deletes only its own objects/bucket. MinIO credentials are
local fixtures. The pinned MinIO image is a test fixture, not a production recommendation.

Expanded integration acceptance plan before stable release:

- Paginated prefix listing, Unicode/quoted object names and opaque multipart ETags.
- Changed content, overwrite during read (`IfMatch` failure), missing and deleted objects.
- Denied list/read, expired credentials, retries, unavailable endpoint and oversized files.
- Kill during pending index replacement; restart and converge without duplicate chunks.
- Real FastEmbed and Docling PDF/DOCX/HTML parsing; model cache cold/warm and offline.
- Restore a stopped-volume backup and compare known queries and document counts.
- Auth rejection, malformed MCP messages and browser console flows across supported OSes.

CI cannot prove these unimplemented acceptance cases. Marked model-enabled tests and
a reproducible evaluation corpus are useful first follow-ups.
