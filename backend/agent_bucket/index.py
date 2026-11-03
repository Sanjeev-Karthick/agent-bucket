import hashlib
import threading
from pathlib import Path
from typing import Any

import lancedb
import pyarrow as arrow
from lancedb.index import FTS
from lancedb.rerankers import RRFReranker

from agent_bucket.embeddings import Embedder
from agent_bucket.models import Hit, SearchRequest


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


class RetrievalService:
    def __init__(self, path: Path, dimensions: int, embedder: Embedder) -> None:
        self.lock = threading.RLock()
        self.embedder = embedder
        self.db = lancedb.connect(str(path))
        schema = arrow.schema(
            [
                arrow.field("id", arrow.string()),
                arrow.field("uri", arrow.string()),
                arrow.field("text", arrow.string()),
                arrow.field("chunk", arrow.int32()),
                arrow.field("vector", arrow.list_(arrow.float32(), dimensions)),
            ]
        )
        self.table: Any = self.db.create_table("chunks", schema=schema, exist_ok=True)
        self.table.create_index("text", config=FTS(), replace=True)

    def count(self) -> int:
        with self.lock:
            return int(self.table.count_rows())

    def replace(self, uri: str, chunks: list[str]) -> None:
        with self.lock:
            vectors = self.embedder.embed(chunks) if chunks else []
            rows = [
                {
                    "id": hashlib.sha256(f"{uri}:{position}".encode()).hexdigest(),
                    "uri": uri,
                    "text": text,
                    "chunk": position,
                    "vector": vector,
                }
                for position, (text, vector) in enumerate(zip(chunks, vectors, strict=True))
            ]
            self.table.delete(f"uri = {sql_literal(uri)}")
            if rows:
                self.table.add(rows)

    def delete(self, uri: str) -> None:
        with self.lock:
            self.table.delete(f"uri = {sql_literal(uri)}")

    def search(self, request: SearchRequest) -> list[Hit]:
        with self.lock:
            if self.table.count_rows() == 0:
                return []
            if request.mode == "keyword":
                query = self.table.search(request.query, query_type="fts", fts_columns="text")
                score_key = "_score"
            else:
                vector = self.embedder.embed([request.query])[0]
                if request.mode == "vector":
                    query = self.table.search(vector).distance_type("cosine")
                    score_key = "_distance"
                else:
                    query = (
                        self.table.search(query_type="hybrid", fts_columns="text")
                        .vector(vector)
                        .text(request.query)
                        .rerank(RRFReranker())
                    )
                    score_key = "_relevance_score"
            rows = query.limit(request.limit).to_list()
            return [
                Hit(
                    id=row["id"],
                    uri=row["uri"],
                    text=row["text"],
                    chunk=row["chunk"],
                    score=(1.0 - float(row[score_key]))
                    if request.mode == "vector"
                    else float(row[score_key]),
                )
                for row in rows
            ]
