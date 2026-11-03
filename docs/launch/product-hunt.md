# Product Hunt launch workspace

Status: placeholders for a future launch. No performance, adoption or availability
claims have been validated. The repository is a developer preview.

Name: **agent-bucket**

Tagline: **Make your object store searchable by AI agents.**

Draft description: Open-source retrieval over existing S3-compatible buckets. Run a
sidecar, sync a chosen prefix and retrieve cited chunks through REST or MCP. V0.1
uses one node and one container: single-node first, scale-out by design.

Demo storyboard (60–90 seconds): start the container → open the console → sync
synthetic documents → search using BM25 → switch to real-model hybrid retrieval →
show a cited MCP tool response → show the current limits and roadmap.

Assets to create before submission:

- Logo source/export: `assets/brand/` (currently references only).
- Gallery: console screenshot, architecture diagram and a source-to-citation demo.
- Demo video and caption file; accessible image descriptions.
- Maker comment explaining the problem, current scope and desired feedback.
- Verified quickstart, support/reporting links and measured benchmark methodology.

Use real-model mode when demonstrating semantic understanding. Never present the
hash fixture as a semantic search model. Ask users for feedback rather than votes.
