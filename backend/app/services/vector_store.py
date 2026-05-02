from __future__ import annotations

import logging
import threading
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import settings


logger = logging.getLogger(__name__)
_init_lock = threading.Lock()
_op_lock = threading.Lock()
_qdrant_client: QdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        with _init_lock:
            if _qdrant_client is None:
                _qdrant_client = QdrantClient(":memory:")
    return _qdrant_client


class VectorStore:
    def __init__(self) -> None:
        self.collection_name = settings.qdrant_collection_name

    @property
    def client(self) -> QdrantClient:
        return get_qdrant_client()

    def ensure_collection(self, vector_size: int) -> None:
        if not self.client.collection_exists(self.collection_name):
            logger.info(
                "qdrant.collection.create collection=%s vector_size=%s",
                self.collection_name,
                vector_size,
            )
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            return

        info = self.client.get_collection(self.collection_name)
        current_size = info.config.params.vectors.size
        if current_size != vector_size:
            logger.warning(
                "qdrant.collection.recreate collection=%s old_vector_size=%s new_vector_size=%s",
                self.collection_name,
                current_size,
                vector_size,
            )
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    def upsert_profile(self, profile_id: str, vector: list[float], payload: dict) -> None:
        with _op_lock:
            self.ensure_collection(len(vector))
            logger.info(
                "qdrant.profile.upsert collection=%s profile_id=%s vector_size=%s source=%s",
                self.collection_name,
                profile_id,
                len(vector),
                payload.get("source"),
            )
            self.client.upsert(
                collection_name=self.collection_name,
                points=[PointStruct(id=self._point_id(profile_id), vector=vector, payload=payload)],
            )

    def search(self, vector: list[float], top_k: int) -> list[dict]:
        with _op_lock:
            self.ensure_collection(len(vector))
            logger.info(
                "qdrant.search.start collection=%s vector_size=%s top_k=%s",
                self.collection_name,
                len(vector),
                top_k,
            )
            response = self.client.query_points(
                collection_name=self.collection_name,
                query=vector,
                limit=top_k,
                with_payload=True,
            )
            hits = [
                {
                    "id": str(hit.id),
                    "score": float(hit.score),
                    "payload": hit.payload or {},
                }
                for hit in response.points
            ]
            logger.info(
                "qdrant.search.done collection=%s hits=%s top_scores=%s",
                self.collection_name,
                len(hits),
                [round(hit["score"], 3) for hit in hits[:5]],
            )
            return hits

    def _point_id(self, profile_id: str) -> str:
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"coffee-ninja:{profile_id}"))
