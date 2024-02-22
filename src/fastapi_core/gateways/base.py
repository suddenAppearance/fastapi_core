import logging
from abc import ABC
from functools import partial
from typing import Callable, ClassVar, Mapping, ParamSpec, Type, TypeVar, Any

import pydantic
from httpx import AsyncClient, Response
from pydantic import AnyHttpUrl, TypeAdapter

from fastapi_core.gateways.exceptions import InterServiceContractMismatchException
from fastapi_core.settings.httpx import HTTPXConfig

P = ParamSpec("P")
T = TypeVar("T")


def create_partial(func: Callable[P, T], *args, **kwargs) -> Callable[P, T]:
    """
    functools.partial(...) wrapper with proper type hinting
    """
    return partial(func, *args, **kwargs)


class BaseGateway(ABC):
    """
    Gateway Base with shortcuts that passes headers for every request
    """

    def __init__(self, client: AsyncClient, headers: Mapping[str, str]):
        self._client = client
        self.headers = self.clear_headers(headers)

        # Shortcuts that substitute headers.
        # Headers could be overriden.
        # If you need to add headers, you can add then to self.headers directly
        self.post = create_partial(self._client.post, headers=self.headers)
        self.get = create_partial(self._client.get, headers=self.headers)
        self.put = create_partial(self._client.put, headers=self.headers)
        self.patch = create_partial(self._client.patch, headers=self.headers)
        self.delete = create_partial(self._client.delete, headers=self.headers)
        self.options = create_partial(self._client.options, headers=self.headers)

    @staticmethod
    def clear_params(params: dict) -> dict:
        """
        Clear ``None`` params.

        :param params: params dictionary to be cleared.
        :returns: cleared params.
        """
        return {k: v for k, v in params.items() if v}

    @staticmethod
    def clear_headers(headers: Mapping[str, str]) -> dict:
        """
        Clear not allowed headers that are passed when proxying

        :param headers: headers to clear.
        :returns: cleared headers.
        """
        not_allowed_headers = ("content-length", "host", "content-type", "user-agent")
        return {k: v for k, v in headers.items() if k.lower() not in not_allowed_headers}

    @staticmethod
    def parse_response_as(schema: Type[T], response: Response, optimistic: bool = False) -> T | None:
        """
        Parse `response` object into `schema` object

        :param schema: Schema to unmarshall response into
        :param response: response object
        :param optimistic: optimistic parse - if True, returns None on failure
        :returns: `schema` object if response is valid
        :raises InterServiceContractMismatchException: `response` validation onto `schema` failed
        :raises httpx.HTTPStatusError: `response` status code greater than or equal 400
        """
        if not response.is_success and not optimistic:
            response.raise_for_status()
        elif not response.is_success and optimistic:
            return None

        try:
            return TypeAdapter(schema).validate_json(response.content)
        except pydantic.ValidationError as e:
            if not optimistic:
                raise InterServiceContractMismatchException(response, e.errors())
            else:
                return None


class PathMappable(ABC):
    path_mapping: ClassVar[dict[str, str]]

    @classmethod
    def get_path(cls, key: str) -> str:
        return cls.path_mapping[key]


logger = logging.getLogger("api.gateway")


async def log_response(response: Response):
    logger.debug(f"\"{response.request.method} {response.url}\" {response.status_code} {response.reason_phrase}")


def get_async_client(url: AnyHttpUrl, **kwargs: Any):
    return AsyncClient(
        base_url=url,
        event_hooks={
            "request": [],
            "response": [log_response],
        },
        timeout=HTTPXConfig().get_timeout(),
        **kwargs
    )
