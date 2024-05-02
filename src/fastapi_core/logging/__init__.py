def get_logger(name: str = None):
    try:
        from loguru import logger
        return logger
    except ImportError:
        from logging import getLogger
        return getLogger(name or __name__)
