from typing import AsyncGenerator, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_core.database.sessions import get_session_factories, get_engines
from fastapi_core.settings.database import DatabaseSettings

db_settings = DatabaseSettings()

create_session, create_async_session = get_session_factories(
    *get_engines(db_settings.DATABASE_URL.replace("+asyncpg", ""), db_settings.DATABASE_URL))


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Session dependency async generator
    :param async_session_factory: async session factory (sessionmaker)
    :return: AsyncSession object
    """
    session = create_async_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        if session:
            await session.close()
