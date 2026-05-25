import os
from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


def _get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        local_db = Path(__file__).resolve().parents[1] / "local.db"
        return f"sqlite+aiosqlite:///{local_db.as_posix()}"

    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)

    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    return database_url


class Base(DeclarativeBase):
    pass


engine: AsyncEngine | None = None
AsyncSessionLocal = async_sessionmaker(
    class_=AsyncSession,
    expire_on_commit=False,
)


def get_engine() -> AsyncEngine:
    global engine

    if engine is None:
        engine = create_async_engine(_get_database_url(), pool_pre_ping=True)
        AsyncSessionLocal.configure(bind=engine)

    return engine


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    get_engine()
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create tables and seed categories when using the local SQLite fallback."""
    from db.models import Category
    from routers.upload import CATEGORY_META

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Category))
        existing = {category.name for category in result.scalars()}
        for name, meta in CATEGORY_META.items():
            if name not in existing:
                session.add(
                    Category(
                        name=name,
                        color_hex=meta["color_hex"],
                        icon_key=meta["icon_key"],
                    )
                )
        await session.commit()
