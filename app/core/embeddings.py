from __future__ import annotations

from sentence_transformers import SentenceTransformer
from sqlalchemy import text

from app.db.base import SessionLocal
from app.db.models import Event

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """Load embedding model singleton."""
    global _model
    if _model is None:
        print("📦 Loading embedding model...")
        _model = SentenceTransformer(MODEL_NAME)
        print("✅ Embedding model loaded")
    return _model


def embed_text(text: str) -> list[float]:
    """Embed text using sentence-transformers."""
    model = get_model()
    return model.encode(text, normalize_embeddings=True).tolist()


def build_event_text(event: Event) -> str:
    """
    Build rich text representation of an event for embedding.
    Combines all available fields for better semantic search.
    """
    parts = []
    if event.title_fr:
        parts.append(event.title_fr)
    if event.title_ar:
        parts.append(event.title_ar)
    if event.description_fr:
        parts.append(event.description_fr)
    if event.description_ar:
        parts.append(event.description_ar)
    if event.wilaya:
        parts.append(event.wilaya)
    if event.commune:
        parts.append(event.commune)
    if event.cost:
        parts.append(event.cost)
    return " ".join(parts)


def upsert_event_embedding(event_id: int, embedding: list[float]) -> None:
    """
    Insert or update embedding for an event.
    Safe to call on create and update.
    """
    db = SessionLocal()
    try:
        db.execute(
            text("""
                INSERT INTO event_embeddings (event_id, embedding)
                VALUES (:event_id, :embedding)
                ON CONFLICT (event_id)
                DO UPDATE SET embedding = EXCLUDED.embedding
            """),
            {"event_id": event_id, "embedding": str(embedding)},
        )
        db.commit()
    except Exception as e:
        print(f"⚠️ Failed to upsert embedding for event {event_id}: {e}")
        db.rollback()
    finally:
        db.close()


def search_similar_events(query: str, limit: int = 5) -> list[int]:
    """
    Embed query and return top matching event IDs from pgvector.
    Returns list of event_ids ordered by similarity.
    """
    query_embedding = embed_text(query)
    db = SessionLocal()
    try:
        result = db.execute(
            text("""
                SELECT event_id
                FROM event_embeddings
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :limit
            """),
            {"embedding": str(query_embedding), "limit": limit},
        )
        return [row[0] for row in result.fetchall()]
    except Exception as e:
        print(f"⚠️ Vector search failed: {e}")
        return []
    finally:
        db.close()
