from typing import TypeVar, Awaitable, Callable, ParamSpec, get_args, get_origin, Type, overload, Literal

from pydantic import TypeAdapter, BaseModel
from sqlalchemy import Select
from sqlalchemy.orm import DeclarativeBase, defer

from fastapi_core.logging import get_logger
from fastapi_core.repositories.base import BaseRepository
from fastapi_core.settings.database import DatabaseSettings

S = TypeVar("S")
M = TypeVar("M", bound=type[DeclarativeBase])
P = ParamSpec("P")

logger = get_logger("api.mappers")

settings = DatabaseSettings()


def _mapped(
    from_model: M | None, to_schema: S, to_list: bool = False, optional: bool = False
) -> Callable[[Callable[P, Select]], Callable[P, Awaitable[S | list[S] | None]]]:
    initial_type = to_schema
    to_schema = TypeAdapter(to_schema)
    try:
        is_pydantic = issubclass(initial_type, BaseModel)
    except TypeError:
        is_pydantic = False

    list_to_schema = TypeAdapter(list[initial_type])

    if is_pydantic and from_model is not None:
        initial_type: Type[BaseModel]
        database_columns: set[str] = set(from_model.__table__.columns.keys())
        schema_columns = initial_type.model_fields.keys()
        extra_columns = database_columns - schema_columns
    else:
        extra_columns = set()

    def decorator(func: Callable[P, Select]) -> Callable[P, Awaitable[S | list[S] | None]]:
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> S | list[S] | None:
            statement = func(*args, **kwargs)
            if extra_columns:
                statement = statement.options(defer(*(getattr(from_model, key) for key in extra_columns)))
            repo: BaseRepository[M] = args[0]
            if settings.SQL_ENGINE_ECHO:
                logger.debug(f"{statement.compile()}")

            result = await repo.execute(statement)

            if from_model is not None:
                result = result.scalars()
            else:
                result = result.mappings()

            if to_list:
                result = result.all()
            else:
                result = result.one_or_none()

            if result is None and optional:
                return result

            if not to_list:
                return to_schema.validate_python(result)
            else:
                return list_to_schema.validate_python(result)

        return wrapper

    return decorator


@overload
def mapped(
    from_model: M | None, to_schema: Type[S], optional: Literal[False] = False
) -> Callable[[Callable[P, Select]], Callable[P, Awaitable[S]]]:
    ...


@overload
def mapped(
    from_model: M | None, to_schema: Type[S], optional: Literal[True] = False
) -> Callable[[Callable[P, Select]], Callable[P, Awaitable[S | None]]]:
    ...


def mapped(
    from_model: M | None, to_schema: Type[S | None], optional: bool = False
) -> Callable[[Callable[P, Select]], Callable[P, Awaitable[S | None]]]:
    if get_origin(to_schema) is list:
        return _mapped(from_model, get_args(to_schema)[0], to_list=True, optional=optional)
    return _mapped(from_model, to_schema, optional=optional)
