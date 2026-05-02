from __future__ import annotations

from threading import RLock
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import settings


_client_lock = RLock()
_qdrant_client: QdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    global _qdrant_client

    if _qdrant_client is None:
        with _client_lock:
            if _qdrant_client is None:
                _qdrant_client = QdrantClient(path=settings.qdrant_path)

    return _qdrant_client


class VectorStore:
    def __init__(self) -> None:
        self.client = get_qdrant_client()
        self.collection_name = settings.qdrant_collection_name

    def ensure_collection(self, vector_size: int) -> None:
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            return

        info = self.client.get_collection(self.collection_name)
        current_size = info.config.params.vectors.size
        if current_size != vector_size:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    def upsert_profile(self, profile_id: str, vector: list[float], payload: dict) -> None:
        self.ensure_collection(len(vector))
        self.client.upsert(
            collection_name=self.collection_name,
            points=[PointStruct(id=self._point_id(profile_id), vector=vector, payload=payload)],
        )

    def search(self, vector: list[float], top_k: int) -> list[dict]:
        self.ensure_collection(len(vector))
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=top_k,
            with_payload=True,
        )
        return [
            {
                "id": str(hit.id),
                "score": float(hit.score),
                "payload": hit.payload or {},
            }
            for hit in response.points
        ]

    def _point_id(self, profile_id: str) -> str:
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"coffee-ninja:{profile_id}"))
