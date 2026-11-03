# ADR 0002: Optional inference and parsing with an offline fixture

Status: accepted for the starter.

Decision: FastEmbed is the initial real embedding provider. Docling handles PDF,
DOCX and HTML. Install these with `uv sync --extra inference --extra parsing`.
The container includes both extras. Tests and the quick demo explicitly select
hash embeddings and text/Markdown data to avoid model downloads. Hash mode is
identified in API responses and the UI and is never evaluated as semantic retrieval.

The MCP adapter uses the official `mcp` package's 1.x FastMCP API with a `<2` bound.
The SDK's separate `fastmcp` package is not a dependency. Migration to the 2.x API
must include transport/auth regression tests; the checked-in lock selects exact versions.

Consequences: model downloads and parser cost are paid only by real deployments.
Optional adapters need separate model-enabled validation before stable release.
Changing embedding identity requires a fresh index to prevent mixed vector spaces.
