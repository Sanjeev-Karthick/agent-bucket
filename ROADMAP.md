# Roadmap

**Single-node first, scale-out by design.** This roadmap records direction, not dates
or delivery commitments. Service interfaces make later replacement possible; they do
not establish distributed correctness or horizontal scaling today.

## V0.1 preview — current starter

- [x] One process/container; SQLite WAL state; local embedded LanceDB.
- [x] One configured demo directory or S3-compatible bucket/prefix.
- [x] Explicit sync jobs, changed-object detection, deletion reconciliation.
- [x] BM25, vector and hybrid retrieval with REST/MCP/UI.
- [x] Optional Docling and FastEmbed adapters; synthetic demo and MinIO test harness.

## Before a stable V0.1 release

- [ ] Verify Docling PDF/DOCX/HTML and real model paths across supported platforms.
- [ ] Parser isolation, deadlines, bounded memory, structured safe diagnostics.
- [ ] Kill/restart, backup/restore and index-corruption tests.
- [ ] Pin container base-image digests; image and dependency vulnerability review.
- [ ] Model prefetch/offline packaging and artifact license inventory.
- [ ] Object version IDs, conditional-list race tests and explicit retry policy.
- [ ] Signed releases, SBOM, container provenance and dedicated conduct contact.
- [ ] Publish reproducible benchmark results; define tested resource envelopes.

## Later single-node improvements

- [ ] Scheduled sync, object notifications, job cancellation and progress.
- [ ] Better structure-aware chunks, metadata filters, rerankers and evaluation corpus.
- [ ] Incremental FTS maintenance, compaction and secure deletion/retention controls.
- [ ] Safer operations UI and configurable MCP gateway allowlists.

## Future scale-out investigation

- [ ] Replace embedded jobs/state with a transactional external control plane.
- [ ] Introduce worker leases, heartbeats, fencing and idempotent publication.
- [ ] Immutable index generations, publication manifests and query snapshot pinning.
- [ ] Separate indexing workers from read/query workers; measure shard routing.
- [ ] Design authorization and tenant isolation before multi-tenant hosting.

Changing SQLite to Postgres alone is insufficient. Shared filesystem access to a
local Lance directory is not a supported distributed deployment.
