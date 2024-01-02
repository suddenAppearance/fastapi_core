import logging
from typing import Type, TypeVar, Callable

from fastapi import Depends
from starlette.requests import Request

from fastapi_core.services.base import BaseServiceWithSession

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
