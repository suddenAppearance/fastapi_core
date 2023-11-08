from logging import Logger
from typing import Any, Mapping, Type, TypeVar

# try/except imports are only for type hinting purposes
try:
    from sqlalchemy.ext.asyncio import AsyncSession
except ImportError:
    AsyncSession = object

# Setting class in settings.py at project root
try:
    from settings import Settings
except ImportError:
    Settings = object

T = TypeVar("T")


class BaseServiceWithSession:
    """Base class with sqlalchemy.ext.asyncio.AsyncSession"""

    def __init__(
        self,
        session: AsyncSession,
        logger: Logger,
        settings: Settings,
        container: Any,
        headers: Mapping[str, str] | None = None,
    ):
        """
        :param session: database session
        :param logger: shared logger
        :param settings: application settings
        :param container: classes container for per request singleton (request.state is suitable)
        :param headers: request headers
        """
        self.session = session
        self.logger = logger
        self.settings = settings
        self._container = container
        self._container.headers = headers or {}

    def factory(self, cls: Type[T]) -> T:
        placeholder = f"_{cls.__name__}"
        if not hasattr(self._container, placeholder):
            setattr(
                self._container, placeholder, cls(self.session, self.logger, self.settings, container=self._container)
            )

        service: cls = getattr(self._container, placeholder)
        return service

    def repo_factory(self, cls: Type[T]) -> T:
        placeholder = f"_{cls.__name__}"
        if not hasattr(self._container, placeholder):
            setattr(self._container, placeholder, cls(self.session))

        repo: cls = getattr(self._container, placeholder)
        return repo

    def gateway_factory(self, cls: Type[T], client) -> T:
        placeholder = f"_{cls.__name__}"
        if not hasattr(self._container, placeholder):
            setattr(self._container, placeholder, cls(client, self._container.headers))

        gateway: cls = getattr(self._container, placeholder)
        return gateway


class BaseServiceWithoutSession:
    """
    Same as BaseServiceWithSession but without `session` and `repo_factory()`
    """
    def __init__(self, logger: Logger, settings: Settings, container: Any, headers: Mapping[str, str] | None = None):
        self.logger = logger
        self.settings = settings
        self._container = container
        self._container.headers = headers or {}

    def factory(self, cls: Type[T]) -> T:
        placeholder = f"_{cls.__name__}"
        if not hasattr(self._container, placeholder):
            setattr(self._container, placeholder, cls(self.logger, self.settings, container=self._container))

        service: cls = getattr(self._container, placeholder)
        return service

    def gateway_factory(self, cls: Type[T], client) -> T:
        placeholder = f"_{cls.__name__}"
        if not hasattr(self._container, placeholder):
            setattr(self._container, placeholder, cls(client, self._container.headers))

        gateway: cls = getattr(self._container, placeholder)
        return gateway
