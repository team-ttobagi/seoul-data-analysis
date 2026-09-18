import pytest

from backend.app.core.database import create_database_engine


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "database_url",
    [
        "postgresql://user:password@localhost/example",
        "postgresql+asyncpg://user:password@localhost/example",
    ],
)
async def test_postgresql_engine_recycles_and_pre_pings_connections(database_url: str):
    engine = create_database_engine(database_url)

    try:
        pool = engine.sync_engine.pool

        assert pool._pre_ping is True
        assert pool._recycle == 1800
    finally:
        await engine.dispose()
