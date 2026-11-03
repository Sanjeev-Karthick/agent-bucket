from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from agent_bucket.parsing import chunk_text
from agent_bucket.state import JobRepository


def test_queue_deduplicates_concurrent_requests_and_recovers(tmp_path: Path) -> None:
    repository = JobRepository(tmp_path / "state.db")
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = list(pool.map(lambda _: repository.enqueue(), range(8)))
    assert len({job.id for job in jobs}) == 1
    job = repository.claim()
    assert job is not None and job.status == "running"
    restarted = JobRepository(tmp_path / "state.db")
    restarted.recover()
    recovered = restarted.claim()
    assert recovered is not None and recovered.id == job.id
    restarted.finish(job.id)
    assert restarted.enqueue().id != job.id


def test_identity_change_requires_fresh_directory(tmp_path: Path) -> None:
    repository = JobRepository(tmp_path / "state.db")
    repository.check_identity({"model": "first"})
    with pytest.raises(ValueError, match="fresh AB_DATA_DIR"):
        repository.check_identity({"model": "second"})


def test_chunking_preserves_text_with_overlap() -> None:
    assert chunk_text("abcdefghij", 6, 2) == ["abcdef", "efghij"]
    assert chunk_text("  ", 6, 2) == []
    with pytest.raises(ValueError):
        chunk_text("data", 6, 6)
