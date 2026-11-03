import json
import platform
import statistics
import tempfile
import time
from pathlib import Path

from agent_bucket.embeddings import HashEmbedder
from agent_bucket.index import RetrievalService
from agent_bucket.models import SearchRequest


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="ab-benchmark-") as directory:
        index = RetrievalService(Path(directory), 384, HashEmbedder(384))
        started = time.perf_counter()
        index.replace(
            "demo://benchmark",
            [
                f"Document {number}: rotate access keys and verify retrieval permissions."
                for number in range(100)
            ],
        )
        ingest = time.perf_counter() - started
        request = SearchRequest(query="rotate access keys", mode="keyword", limit=5)
        for _ in range(10):
            index.search(request)
        timings = []
        for _ in range(100):
            started = time.perf_counter()
            assert len(index.search(request)) == 5
            timings.append((time.perf_counter() - started) * 1000)
        ordered = sorted(timings)
        print(
            json.dumps(
                {
                    "fixture_only": True,
                    "python": platform.python_version(),
                    "platform": platform.platform(),
                    "chunks": index.count(),
                    "concurrency": 1,
                    "mode": "keyword",
                    "ingest_seconds": ingest,
                    "queries": len(timings),
                    "p50_ms": statistics.median(timings),
                    "p95_ms": ordered[94],
                    "p99_ms": ordered[98],
                    "raw_ms": timings,
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
