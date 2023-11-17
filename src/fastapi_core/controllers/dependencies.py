import logging
from typing import Type, TypeVar, Callable, AsyncGenerator

from fastapi import Depends
from starlette.requests import Request

from fastapi_core.services.base import BaseServiceWithSession, TasksCollection

try:
    from sqlalchemy.ext.asyncio import AsyncSession
    from fastapi_core.database.dependencies import get_session

except ImportError:
    get_session = NotImplemented
    AsyncSession = NotImplemented

T = TypeVar("T")


def get_service(service: Type[T]) -> Callable[..., T]:
    logger = logging.getLogger(f"api.{service.__name__}")

    db = issubclass(service, BaseServiceWithSession)

    def _get_service_with_db_session(request: Request, session: AsyncSession = Depends(get_session)):
        return service(session=session, logger=logger, container=request.state, headers=request.headers)

    def _get_service_without_db_session(request: Request):
        return service(logger=logger, container=request.state, headers=request.headers)

    return _get_service_with_db_session if db else _get_service_without_db_session


async def run_on_success(request: Request) -> AsyncGenerator[None, None]:
    logger = logging.getLogger("api.run_on_success")
    """
    Task pool, that can only be executed after a successful response
    """

    # get or init tasks pool
    if not hasattr(request.state, "_on_success"):
        setattr(request.state, "_on_success", TasksCollection(logger=logger))
    tasks: TasksCollection = getattr(request.state, "_on_success")

    try:
        # wait for response
        yield

        # process tasks after response
        logger.debug(
            f"{len(tasks)} task(s) collected during request."
            f" {len(tasks.async_tasks)} coro(s) and {len(tasks.sync_tasks)} sync tasks"
        )
        await tasks.process_all()

    except Exception as exc:
        logger.error(f"Running tasks error: {exc.__class__.__name__}: {exc}", exc_info=True)
        tasks.cancel()
        raise
