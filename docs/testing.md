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
local fixtures. The MinIO fixture builds the pinned upstream
`RELEASE.2025-10-15T17-29-55Z` source because the upstream registry images are no longer
available. Its initial Go build can take several minutes. MinIO remains separately
licensed under AGPL-3.0; it is a test dependency and is not bundled into agent-bucket.
See [upstream source distribution](https://github.com/minio/minio#source-only-distribution).

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
