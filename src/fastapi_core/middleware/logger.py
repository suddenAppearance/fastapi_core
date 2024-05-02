from typing import Callable, Awaitable

from fastapi.requests import Request
from loguru import logger


async def json_exceptions_wrapper_middleware(request: Request, call_next: Callable[[Request], Awaitable]):
    """
    JSONResponse exception wrapping
    """
    with logger.contextualize(
        method=request.method,
        path=request.url.path,
        query=request.url.query,
        user=request.user.sub if request.user else None
    ):
        return await call_next(request)
