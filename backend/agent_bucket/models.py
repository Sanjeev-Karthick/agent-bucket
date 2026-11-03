from typing import Literal

from pydantic import BaseModel, Field

SearchMode = Literal["keyword", "vector", "hybrid"]


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000, pattern=r"\S")
    mode: SearchMode = "hybrid"
    limit: int = Field(default=5, ge=1, le=50)


class Hit(BaseModel):
    id: str
    uri: str
    text: str
    chunk: int
    score: float


class SearchResponse(BaseModel):
    hits: list[Hit]
    mode: SearchMode
    embedding_provider: str


class Job(BaseModel):
    id: str
    status: Literal["queued", "running", "succeeded", "failed"]
    created_at: str
    finished_at: str | None = None
    indexed: int = 0
    skipped: int = 0
    deleted: int = 0
    error: str | None = None


class Status(BaseModel):
    version: str
    source: str
    embedding_provider: str
    documents: int
    chunks: int
    deployment: str = "single-node first, scale-out by design"
