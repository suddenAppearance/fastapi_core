import inspect
from logging import Logger
from typing import Any, Mapping, Type, TypeVar, Coroutine, Callable

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


class TasksCollection:
    def __init__(self, logger: Logger):
        self.async_tasks: list[Coroutine] = []
        self.sync_tasks: list[Callable] = []
        self.logger = logger

    def __len__(self):
        return len(self.async_tasks) + len(self.sync_tasks)

    def add_task(self, task: Coroutine | Callable):
        """
        Pass either coro or functools.partial(...) wrapped synchronous function to add task to pool
        They will be executed after request is succeeded
        """
        if inspect.isawaitable(task):
            is_awaitable = True
            self.async_tasks.append(task)
        else:
            is_awaitable = False
            self.sync_tasks.append(task)

            # functools.partial(...) does not set __name__ property
            try:
                task.__name__ = task.func.__name__
            except AttributeError:
                task.__name__ = "<unknown>"

        self.logger.debug(
            f"{task.__name__} was added to task pool. Assuming it is {'awaitable' if is_awaitable else 'synchronous'}"
        )

    def add_tasks(self, *tasks: Coroutine | Callable):
        """
        Shortcut for adding multiple tasks
        """
        for task in tasks:
            self.add_task(task)

    async def process_all(self):
        self.logger.debug(f"Initiating tasks processing... {len(self)} tasks to process")
        for coro in self.async_tasks:
            self.logger.debug(f"awaiting task {coro.__name__}...")
            await coro
        for task in self.sync_tasks:
            if hasattr(task, "func") and hasattr(task.func, "__self__"):
                task.__name__ = task.func.__self__.__name__
            self.logger.debug(f"executing task {task.__name__} ")
            task()

    def cancel(self):
        self.logger.debug(f"Canceling {len(self)} tasks")

        for coro in self.async_tasks:
            try:
                # Closing coro so there is no warning that coro was never awaited
                coro.close()
            except Exception:  # noqa
                pass

        self.async_tasks.clear()
        self.sync_tasks.clear()


class BaseService:
    """
    Base class of any service
    """

    def __init__(self, container: Any, headers: Mapping[str, str] | None = None):
        """
        :param container: classes container for per request singleton (request.state is suitable)
        :param headers: request headers
        """
        self._container = container
        self._container.headers = headers or {}

    def gateway_factory(self, cls: Type[T], client) -> T:
        placeholder = f"_{cls.__name__}"
        if not hasattr(self._container, placeholder):
            setattr(self._container, placeholder, cls(client, self._container.headers))

        gateway: cls = getattr(self._container, placeholder)
        return gateway

    @property
    def on_success(self) -> TasksCollection:
        if not hasattr(self._container, "_on_success"):
            raise AttributeError("Tried to access on_success dependency, which is not injected in container")
        return getattr(self._container, "_on_success")


class BaseServiceWithSession(BaseService):
    """Base class with sqlalchemy.ext.asyncio.AsyncSession"""

    def __init__(
        self,
        session: AsyncSession,
        logger: Logger,
        container: Any,
        headers: Mapping[str, str] | None = None,
    ):
        """
        :param session: database session
        :param logger: shared logger
        """
        self.session = session
        self.logger = logger
        super().__init__(container, headers)

    def factory(self, cls: Type[T]) -> T:
        placeholder = f"_{cls.__name__}"
        if not hasattr(self._container, placeholder):
            setattr(self._container, placeholder, cls(self.session, self.logger, container=self._container))

        service: cls = getattr(self._container, placeholder)
        return service

    def repo_factory(self, cls: Type[T]) -> T:
        placeholder = f"_{cls.__name__}"
        if not hasattr(self._container, placeholder):
            setattr(self._container, placeholder, cls(self.session))

        repo: cls = getattr(self._container, placeholder)
        return repo


class BaseServiceWithoutSession(BaseService):
    """
    Same as BaseServiceWithSession but without `session` and `repo_factory()`
    """

    def __init__(self, logger: Logger, container: Any, headers: Mapping[str, str] | None = None):
        self.logger = logger
        super().__init__(container, headers)

    def factory(self, cls: Type[T]) -> T:
        placeholder = f"_{cls.__name__}"
        if not hasattr(self._container, placeholder):
            setattr(self._container, placeholder, cls(self.logger, container=self._container))

        service: cls = getattr(self._container, placeholder)
        return service
