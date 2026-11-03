import logging
from pathlib import Path

from agent_bucket.config import Settings
from agent_bucket.index import RetrievalService
from agent_bucket.parsing import SUPPORTED, DocumentParser, chunk_text
from agent_bucket.state import JobRepository
from agent_bucket.storage import StorageAdapter

logger = logging.getLogger(__name__)


class SyncPlanner:
    def __init__(
        self,
        settings: Settings,
        source: StorageAdapter,
        repository: JobRepository,
        retrieval: RetrievalService,
    ) -> None:
        self.settings = settings
        self.source = source
        self.repository = repository
        self.retrieval = retrieval
        self.parser = DocumentParser()

    def run_next(self) -> bool:
        job = self.repository.claim()
        if job is None:
            return False
        indexed = skipped = deleted = 0
        try:
            inventory = self.source.inventory()
            known = self.repository.objects()
            seen = set()
            for item in inventory:
                seen.add(item.uri)
                if Path(item.key).suffix.lower() not in SUPPORTED:
                    skipped += 1
                    continue
                if known.get(item.uri) == item.etag:
                    skipped += 1
                    continue
                text = self.parser.parse(item.key, self.source.read(item))
                chunks = chunk_text(text, self.settings.chunk_chars, self.settings.chunk_overlap)
                self.repository.remember(item.uri, "pending-reindex")
                self.retrieval.replace(item.uri, chunks)
                self.repository.remember(item.uri, item.etag)
                indexed += 1
            for uri in known.keys() - seen:
                self.retrieval.delete(uri)
                self.repository.forget(uri)
                deleted += 1
            self.repository.finish(job.id, indexed, skipped, deleted)
        except Exception as exception:
            logger.error("Sync %s failed (%s)", job.id, type(exception).__name__)
            self.repository.finish(
                job.id,
                indexed,
                skipped,
                deleted,
                error=f"{type(exception).__name__}: sync failed; check source and model setup",
            )
        return True
