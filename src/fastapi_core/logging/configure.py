from logging import Handler

from loguru import logger


def configure_logger(sink: Handler):
    logger.add(sink)
