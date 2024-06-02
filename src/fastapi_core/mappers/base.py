from typing import TypeVar, Awaitable, Callable, ParamSpec, get_args, get_origin, Type

from pydantic import TypeAdapter
from sqlalchemy import Select
from sqlalchemy.orm import DeclarativeBase, defer

from fastapi_core.repositories.base import BaseRepository

S = TypeVar("S")
M = TypeVar("M", bound=type[DeclarativeBase])
P = ParamSpec("P")


def _mapped(
    from_model: M, to_schema: S, to_list: bool = False, optional: bool = False
) -> Callable[[Callable[P, Select]], Callable[P, Awaitable[S | list[S] | None]]]:
    to_schema = TypeAdapter(to_schema)
    list_to_schema = TypeAdapter(list[S])
    database_columns: set[str] = set(from_model.__table__.columns.keys())
    schema_columns = to_schema.core_schema["cls"].model_fields.keys()
    extra_columns = database_columns - schema_columns

    def decorator(func: Callable[P, Select]) -> Callable[P, Awaitable[S | list[S] | None]]:
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> S | list[S] | None:
            statement = func(*args, **kwargs)
            statement = statement.options(defer(*(getattr(from_model, key) for key in extra_columns)))
            repo: BaseRepository[M] = args[0]
            if to_list:
                result = await repo.all(statement)
            elif optional:
                result = await repo.one_or_none(statement)
            else:
                result = await repo.one(statement)

            if result is None:
                return None

            if not to_list:
                return to_schema.validate_python(result)
            else:
                return list_to_schema.validate_python(result)

        return wrapper

    return decorator


def mapped(from_model: M, to_schema: Type[S]) -> Callable[[Callable[P, Select]], Callable[P, Awaitable[S]]]:
    if get_origin(to_schema) is list:
        return _mapped(from_model, to_schema, to_list=True)
    elif any(t is type(None) for t in get_args(to_schema)):
        return _mapped(from_model, to_schema, optional=True)
    return _mapped(from_model, to_schema)
