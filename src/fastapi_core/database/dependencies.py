from typing import AsyncGenerator, Callable

from sqlalchemy.ext.asyncio import AsyncSession


async def get_session(async_session_factory: Callable[[], AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
    """
    Session dependency async generator
    :param async_session_factory: async session factory (sessionmaker)
    :return: AsyncSession object
    """
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        if session:
            await session.close()
