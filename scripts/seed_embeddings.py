from __future__ import annotations

from app.db.base import SessionLocal
from app.db.models import Event
from app.core.embeddings import build_event_text, embed_text, upsert_event_embedding


def seed() -> None:
    """Seed embeddings for all active events."""
    db = SessionLocal()
    try:
        events = db.query(Event).filter(Event.is_active.is_(True)).all()
        print(f"Seeding embeddings for {len(events)} events...")
        for event in events:
            text = build_event_text(event)
            embedding = embed_text(text)
            upsert_event_embedding(event.id, embedding)
            title = event.title_fr or event.title_ar or event.title or "Unknown"
            print(f"✅ Embedded event {event.id}: {title}")
        print("✅ All embeddings seeded")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
