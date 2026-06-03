from __future__ import annotations

import httpx

from app.core.embeddings import search_similar_events
from app.db.base import SessionLocal
from app.db.models import Event

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"


def build_context(events: list[Event]) -> str:
    """Build a context string from matched events for LLM prompt."""
    if not events:
        return "No events found."
    lines = []
    for e in events:
        title = e.title_fr or e.title_ar or e.title or "Unknown"
        desc = e.description_fr or e.description_ar or ""
        date_str = e.date_begin.strftime("%Y-%m-%d") if e.date_begin else "TBD"
        lines.append(
            f"- {title} | {e.wilaya}, {e.commune} | {date_str} | "
            f"Cost: {e.cost or 'Free'} | {desc[:100]}"
        )
    return "\n".join(lines)


async def chat(user_message: str, lang: str = "fr") -> dict:
    """
    Full RAG pipeline:
    1. Search pgvector for relevant events
    2. Build context
    3. Call Ollama mistral
    4. Return answer + matched event IDs
    """
    db = SessionLocal()
    try:
        event_ids = search_similar_events(user_message, limit=5)
        events: list[Event] = []
        if event_ids:
            events = (
                db.query(Event)
                .filter(Event.id.in_(event_ids), Event.is_active.is_(True))
                .all()
            )

        context = build_context(events)

        prompt = f"""You are a helpful assistant for ODEJ, the Algerian youth organization.
You help young people find events, activities, and opportunities near them.
Answer in the same language the user wrote in (French, Arabic, or Tamazight).
Be concise and friendly.

Available events:
{context}

User question: {user_message}

Answer:"""

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            result = response.json()
            answer = result.get("response", "").strip()

        return {
            "answer": answer,
            "matched_event_ids": event_ids,
            "events_used": len(events),
        }

    except Exception as e:
        print(f"⚠️ Chat failed: {e}")
        return {
            "answer": "Sorry, I am currently unavailable. Please try again later.",
            "matched_event_ids": [],
            "events_used": 0,
        }
    finally:
        db.close()
