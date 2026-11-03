import hashlib
import math
import re
from typing import Any, Protocol

from agent_bucket.config import Settings


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class HashEmbedder:
    """Deterministic lexical fixture for offline demos; provides no semantic understanding."""

    def __init__(self, dimensions: int) -> None:
        self.dimensions = dimensions

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        for text in texts:
            vector = [0.0] * self.dimensions
            for token in re.findall(r"\w+", text.lower()):
                digest = hashlib.sha256(token.encode()).digest()
                index = int.from_bytes(digest[:4]) % self.dimensions
                vector[index] += 1.0 if digest[4] % 2 else -1.0
            norm = math.sqrt(sum(value * value for value in vector)) or 1.0
            vectors.append([value / norm for value in vector])
        return vectors


class FastEmbedder:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model: Any = None

    def embed(self, texts: list[str]) -> list[list[float]]:
        if self.model is None:
            from fastembed import TextEmbedding

            self.model = TextEmbedding(
                model_name=self.settings.embedding_model,
                cache_dir=str(self.settings.data_dir / "models"),
                threads=2,
            )
        vectors = [vector.tolist() for vector in self.model.embed(texts)]
        if any(len(vector) != self.settings.embedding_dimensions for vector in vectors):
            raise ValueError("Model dimensions differ from AB_EMBEDDING_DIMENSIONS")
        return vectors
