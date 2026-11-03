# Benchmark methodology

No performance claims are published for this starter. `make benchmark` runs a small
synthetic keyword-search harness against local LanceDB and prints JSON. Results are
not committed by default. This isolates retrieval cost; it does not measure S3,
Docling, model inference, HTTP/MCP overhead or meaningful semantic quality.

Before publishing measurements, record exact commit/lockfiles, CPU, RAM, disk,
OS, Python, corpus source/license, document/chunk counts and size distribution,
model/version/dimensions, mode, top-k, index parameters and concurrency.

Measure cold and warm startup/model caches separately. Run at least three independent
trials. Report ingestion throughput, peak RSS and disk amplification, then warm-query
p50/p95/p99 and error counts at stated concurrency. Keep raw measurements and disclose
whether queries overlap training/tuning data. For quality, use held-out judged queries
with Recall@k, MRR and nDCG, compare BM25/vector/hybrid on identical chunks, and include
failure examples. Never use hash vectors to claim semantic quality.

Do not extrapolate this single-thread fixture to production capacity or distributed scale.
