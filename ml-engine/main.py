import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import init_db
from routers.insights import router as insights_router
from routers.stats import router as stats_router
from routers.transactions import router as transactions_router
from routers.upload import router as upload_router
from services.categorizer import categorizer


def _allowed_origins() -> list[str]:
    raw = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:3001,"
        "http://127.0.0.1:3000,http://127.0.0.1:3001,"
        "http://[::1]:3000,http://[::1]:3001",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


app = FastAPI(title="HisaabFlow ML Engine", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(stats_router)
app.include_router(insights_router)
app.include_router(transactions_router)


@app.get("/health")
async def health_check():
    try:
        from db.database import get_engine

        db_connected = False
        try:
            from sqlalchemy import text

            async with get_engine().connect() as conn:
                await conn.execute(text("SELECT 1"))
            db_connected = True
        except Exception:
            db_connected = False

        return {
            "status": "ok",
            "model_loaded": categorizer.pipeline is not None,
            "db_connected": db_connected,
        }
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}
