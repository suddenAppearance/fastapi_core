from typing import AsyncGenerator, Callable

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from fastapi_core.database.sessions import get_session_factories, get_engines
from fastapi_core.settings.database import DatabaseSettings

db_settings = DatabaseSettings()


def overridable_get_session_factories():
    return get_session_factories(
        *get_engines(db_settings.DATABASE_URL.replace("+asyncpg", ""), db_settings.DATABASE_URL)
    )


async def get_session(
    session_factories: tuple[Callable[[], Session], Callable[[], AsyncSession]] = Depends(
        overridable_get_session_factories
    )
) -> AsyncGenerator[AsyncSession, None]:
    """
    Session dependency async generator
    """
    _, create_async_session = session_factories
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
