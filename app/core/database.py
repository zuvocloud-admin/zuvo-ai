from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from app.core.config import settings
from app.core.logging import logger

# Base Model for all DB entities
Base = declarative_base()

# Configure Async Engine
engine_kwargs = {"echo": settings.database.echo_sql}
if "sqlite" in settings.database.url:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_size"] = settings.database.pool_size
    engine_kwargs["max_overflow"] = settings.database.max_overflow

async_engine = create_async_engine(settings.database.url, **engine_kwargs)

# Async Session Factory
AsyncSessionFactory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency provider for FastAPI route handlers."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session rollback due to exception: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """Initializes schema tables if not present."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema initialized successfully.")
