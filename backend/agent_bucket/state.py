import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from agent_bucket.models import Job


def now() -> str:
    return datetime.now(UTC).isoformat()


class JobRepository:
    def __init__(self, path: Path) -> None:
        self.path = path
        with self.connection() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS objects (uri TEXT PRIMARY KEY, etag TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY, status TEXT NOT NULL, created_at TEXT NOT NULL,
                    finished_at TEXT, indexed INTEGER NOT NULL DEFAULT 0,
                    skipped INTEGER NOT NULL DEFAULT 0, deleted INTEGER NOT NULL DEFAULT 0,
                    error TEXT
                );
                CREATE UNIQUE INDEX IF NOT EXISTS one_active_sync ON jobs ((1))
                    WHERE status IN ('queued', 'running');
            """)

    @contextmanager
    def connection(self) -> Any:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA synchronous=FULL")
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def check_identity(self, identity: dict[str, Any]) -> None:
        serialized = json.dumps(identity, sort_keys=True)
        with self.connection() as connection:
            row = connection.execute("SELECT value FROM metadata WHERE key='identity'").fetchone()
            if row and row["value"] != serialized:
                raise ValueError("Source/model/chunk settings changed. Use a fresh AB_DATA_DIR.")
            connection.execute(
                "INSERT OR IGNORE INTO metadata VALUES ('identity', ?)", (serialized,)
            )

    def recover(self) -> None:
        with self.connection() as connection:
            connection.execute("UPDATE jobs SET status='queued' WHERE status='running'")

    def enqueue(self) -> Job:
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM jobs WHERE status IN ('queued', 'running')"
            ).fetchone()
            if row:
                return Job(**dict(row))
            job = Job(id=uuid4().hex, status="queued", created_at=now())
            connection.execute(
                "INSERT INTO jobs (id, status, created_at) VALUES (?, ?, ?)",
                (job.id, job.status, job.created_at),
            )
            return job

    def claim(self) -> Job | None:
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT * FROM jobs WHERE status='queued' LIMIT 1").fetchone()
            if row is None:
                return None
            connection.execute("UPDATE jobs SET status='running' WHERE id=?", (row["id"],))
            return Job(**(dict(row) | {"status": "running"}))

    def finish(
        self,
        job_id: str,
        indexed: int = 0,
        skipped: int = 0,
        deleted: int = 0,
        error: str | None = None,
    ) -> None:
        with self.connection() as connection:
            connection.execute(
                "UPDATE jobs SET status=?, finished_at=?, indexed=?, skipped=?, deleted=?, "
                "error=? WHERE id=?",
                (
                    "failed" if error else "succeeded",
                    now(),
                    indexed,
                    skipped,
                    deleted,
                    error,
                    job_id,
                ),
            )

    def jobs(self) -> list[Job]:
        with self.connection() as connection:
            return [
                Job(**dict(row))
                for row in connection.execute(
                    "SELECT * FROM jobs ORDER BY created_at DESC LIMIT 50"
                )
            ]

    def get_job(self, job_id: str) -> Job | None:
        with self.connection() as connection:
            row = connection.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
            return Job(**dict(row)) if row else None

    def objects(self) -> dict[str, str]:
        with self.connection() as connection:
            return dict(connection.execute("SELECT uri, etag FROM objects").fetchall())

    def forget(self, uri: str) -> None:
        with self.connection() as connection:
            connection.execute("DELETE FROM objects WHERE uri=?", (uri,))

    def remember(self, uri: str, etag: str) -> None:
        with self.connection() as connection:
            connection.execute("INSERT OR REPLACE INTO objects VALUES (?, ?)", (uri, etag))
