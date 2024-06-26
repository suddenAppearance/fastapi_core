import logging
import sys
from logging import Handler

from loguru import logger
from loguru._defaults import LOGURU_FORMAT

from fastapi_core.logging.handlers import InterceptHandler


def configure_logger(sink: Handler | None = None):
    sink = sink or InterceptHandler()

    # This makes only uvicorn.access and uvicorn.error loggers to have loguru sinks
    # Thus avoiding duplicate log messages due to root uvicorn logger logging propagated logs from .access and .error
    loggers = (
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith("uvicorn")
    )
    for uvicorn_logger in loggers:
        uvicorn_logger.handlers = [sink]
    logging.getLogger("uvicorn").handlers = []

    logger.configure(
        handlers=[{"sink": sys.stderr, "level": logging.DEBUG, "format": LOGURU_FORMAT, "enqueue": True}]
    )
