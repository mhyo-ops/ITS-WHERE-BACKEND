from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, OptimizersConfigDiff, VectorParams

from ..core.config import settings

VECTOR_SIZE = 768

_client: QdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
    )


def ensure_collection() -> None:
    """
    Creates the Qdrant collection if it doesn't exist.
    Called once at startup.
    Enables quantization for lower memory usage (eco argument).
    """
    client = get_client()
    existing = [c.name for c in client.get_collections().collections]

    if settings.QDRANT_COLLECTION not in existing:
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            optimizers_config=OptimizersConfigDiff(indexing_threshold=10000),
        )
        print(f"✅ Qdrant collection '{settings.QDRANT_COLLECTION}' created")
    else:
        print(f"✅ Qdrant collection '{settings.QDRANT_COLLECTION}' already exists")


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = get_qdrant_client()
    return _client
