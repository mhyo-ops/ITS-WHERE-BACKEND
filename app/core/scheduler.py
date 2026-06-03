import asyncio
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

from app.cache.redis_client import get_redis
from app.core.email import send_reminder_email
from app.db.base import SessionLocal
from app.db.models import Event, user_registered_events

scheduler = AsyncIOScheduler(timezone="UTC")


def _get_redis_key(event_id: int) -> str:
    return f"reminder_sent:event:{event_id}"


async def _process_event_reminders() -> None:
    db: Session = SessionLocal()
    try:
        redis = await get_redis()
        now = datetime.utcnow()
        tomorrow = now + timedelta(days=1)

        events = (
            db.query(Event)
            .filter(Event.start_date >= tomorrow.replace(hour=0, minute=0, second=0, microsecond=0))
            .filter(Event.start_date < tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999))
            .all()
        )

        for event in events:
            redis_key = _get_redis_key(event.id)
            already_sent = await redis.get(redis_key)
            if already_sent:
                continue

            for user in event.registered_users:
                if not user.email:
                    continue

                event_date_str = event.start_date.strftime("%Y-%m-%d %H:%M UTC")
                await send_reminder_email(user.email, event.title, event_date_str, event.address)

            await redis.set(redis_key, "1", ex=60 * 60 * 24)
    except Exception as exc:
        print(f"⚠️ Reminder scheduler error: {exc}")
    finally:
        db.close()


async def _run_event_reminders() -> None:
    await _process_event_reminders()


def start_scheduler() -> None:
    if not scheduler.running:
        scheduler.add_job(
            lambda: asyncio.create_task(_run_event_reminders()),
            trigger="cron",
            hour=7,
            minute=0,
            id="daily_event_reminders",
            replace_existing=True,
        )
        scheduler.start()
        print("✅ Reminder scheduler started")


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("✅ Reminder scheduler stopped")
