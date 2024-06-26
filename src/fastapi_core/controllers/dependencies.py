from typing import Type, TypeVar, Callable

from starlette.requests import Request

from fastapi_core.logging import get_logger
from fastapi_core.services.base import BaseServiceWithSession

try:
    from sqlalchemy.ext.asyncio import AsyncSession

except ImportError:
    AsyncSession = NotImplemented

T = TypeVar("T")


def get_service(service: Type[T]) -> Callable[..., T]:
    logger = get_logger(f"api.{service.__name__}")

    db = issubclass(service, BaseServiceWithSession)

    def _get_service_with_db_session(request: Request):
        return service(session=request.state.session, logger=logger, container=request.state, headers=request.headers)

    def _get_service_without_db_session(request: Request):
        return service(logger=logger, container=request.state, headers=request.headers)

    return _get_service_with_db_session if db else _get_service_without_db_session
