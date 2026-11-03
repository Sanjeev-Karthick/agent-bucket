# Deploying agent-bucket V0.1

Run one container with one Uvicorn process and a persistent local volume. SQLite WAL stores job state and the object manifest. LanceDB stores chunks, full-text indexes, and vectors on the same volume.

V0.1 is single-node first, scale-out by design. It has no distributed query routing, shared queue, high availability, or multi-tenant authorization. Back up the complete volume while the service is stopped.
