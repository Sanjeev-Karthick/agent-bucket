# ADR 0001: Single-node first, scale-out by design

Status: accepted for V0.1 preview.

Context: developers want to expose existing object stores to agents without operating
a separate database, queue and search cluster.

Decision: ship one container with FastAPI, the official Python MCP SDK, one worker,
SQLite WAL and local LanceDB. Keep storage, jobs, parsing, embeddings and retrieval
behind service boundaries. Use a process lock and one worker process.

Consequences: low setup burden, persistent local state and straightforward recovery;
all throughput and availability are limited to one host. Distribution requires a
new control plane, fencing, index generations and consistent query publication.
Interfaces reduce coupling but do not promise a drop-in distributed upgrade.
