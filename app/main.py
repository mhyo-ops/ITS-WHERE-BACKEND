from __future__ import annotations

from fastapi import FastAPI

from .api.auth import router as auth_router
from .api.categories import router as categories_router
from .api.chat import router as chat_router
from .api.events import router as events_router
from .api.metrics import router as metrics_router
from .api.users import router as users_router
from .core.config import settings
from .core.scheduler import shutdown_scheduler, start_scheduler
from .core.translation import download_packages
from .db.init_db import init_db

app = FastAPI()
app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(chat_router)
app.include_router(events_router)
app.include_router(users_router)
app.include_router(metrics_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "database": "postgresql",
        "app": settings.APP_NAME,
    }


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    start_scheduler()
    try:
        download_packages()
    except Exception as e:
        print(f"⚠️ Translation models unavailable: {e}")


@app.on_event("shutdown")
def on_shutdown() -> None:
    shutdown_scheduler()
