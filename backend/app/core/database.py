from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from backend.app.core.config import settings


def create_database_engine(database_url: str) -> AsyncEngine:
    """Create the application engine with PostgreSQL connection safeguards."""
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://", "postgresql+asyncpg://", 1
        )

    return create_async_engine(
        database_url,
        echo=False,
        future=True,
        pool_pre_ping=True,
        pool_recycle=1800,
    )


engine = create_database_engine(settings.DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def _register_all_models() -> None:
    """Import every domain model module so SQLAlchemy can resolve string-based relationships."""
    from backend.app.domain.trade_area import models as _trade_area_models  # noqa: F401
    from backend.app.domain.industry import models as _industry_models  # noqa: F401
    from backend.app.domain.sales import models as _sales_models  # noqa: F401
    from backend.app.domain.district import models as _district_models  # noqa: F401
    from backend.app.domain.store import models as _store_models  # noqa: F401


_register_all_models()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
