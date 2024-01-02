import logging
from typing import Awaitable, Callable, Any

from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession


class LazySession:
    def __init__(self, factory: Callable[[], AsyncSession], logger: logging.Logger):
        self._factory = factory
        self._logger = logger
        self.session: AsyncSession | None = None

    def __getattr__(self, key: str) -> Any:
        if not self.session:
            self.session = self._factory()
            self._logger.debug(f"Started new session {self.session}")

        return getattr(self.session, key)


def transactional_middleware_factory(create_async_session: Callable[[], AsyncSession]):
    logger = logging.getLogger("api.middleware.session")

    lazy_session = LazySession(factory=create_async_session, logger=logger)

    async def transactional_middleware(request: Request, call_next: Callable[[Request], Awaitable]):
        request.state.session = lazy_session
        try:
            response = await call_next(request)
            if lazy_session.session:
                await lazy_session.session.commit()
                logger.debug(f"Transaction committed for session {lazy_session.session}")

            return response
        except Exception:
            if lazy_session.session:
                await lazy_session.session.rollback()
                logger.debug(f"Transaction rolled back for session {lazy_session.session}")
            raise
        finally:
            if lazy_session.session:
                await lazy_session.session.close()
                logger.debug(f"Session {lazy_session.session} closed")

    return transactional_middleware
