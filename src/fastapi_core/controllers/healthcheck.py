from typing import Callable

from fastapi import FastAPI
from starlette.responses import Response


def default_healthcheck() -> Response:
    return Response(status_code=204)


def add_healthcheck_controller(app: FastAPI, func: Callable = default_healthcheck, route: str = "/healthcheck/"):
    app.get(route)(func)
