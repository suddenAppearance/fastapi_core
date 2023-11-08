import logging
from logging import Logger
from typing import Type, TypeVar, Callable

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from fastapi_core.database.dependencies import get_session

T = TypeVar("T")


def get_service(service: Type[T], db=True) -> Callable[..., T]:
    logger = logging.getLogger(service.__name__)

    def _get_service_with_db_session(
        request: Request,
        session: AsyncSession = Depends(get_session),
        logger: Logger = logger,
    ):
        return service(
            session=session, logger=logger, container=request.state, headers=request.headers
        )

    def _get_service_without_db_session(
        request: Request,
        logger: Logger = logger,
    ):
        return service(logger=logger, container=request.state, headers=request.headers)

    return _get_service_with_db_session if db else _get_service_without_db_session
