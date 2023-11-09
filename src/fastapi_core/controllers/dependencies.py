import logging
from typing import Type, TypeVar, Callable

from fastapi import Depends
from starlette.requests import Request

try:
    from sqlalchemy.ext.asyncio import AsyncSession
    from fastapi_core.database.dependencies import get_session

    db = True
except ImportError:
    get_session = NotImplemented
    AsyncSession = NotImplemented

    db = False

T = TypeVar("T")


def get_service(service: Type[T]) -> Callable[..., T]:
    logger = logging.getLogger(service.__name__)

    def _get_service_with_db_session(request: Request, session: AsyncSession = Depends(get_session)):
        return service(session=session, logger=logger, container=request.state, headers=request.headers)

    def _get_service_without_db_session(request: Request):
        return service(logger=logger, container=request.state, headers=request.headers)

    return _get_service_with_db_session if db else _get_service_without_db_session
