import traceback
from typing import Callable, Awaitable

from starlette.requests import Request
from starlette.responses import JSONResponse


async def json_exceptions_wrapper_middleware(request: Request, call_next: Callable[[Request], Awaitable]):
    """
    JSONResponse exception wrapping
    """
    try:
        return await call_next(request)
    except Exception as exc:  # noqa
        return JSONResponse(
            {"message": f"{exc.__class__.__name__}: {exc}", "traceback": traceback.format_exception(exc)}, 500
        )
