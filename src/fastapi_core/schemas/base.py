from typing import TypeVar, Annotated

from pydantic import BaseModel, Field

from fastapi_core.settings.app import APISettings

T = TypeVar('T')


class PaginatedRequestSchema:
    page: Annotated[int, Field(ge=1)]
    page_size: Annotated[int, Field(ge=1)]


class PaginatedResponseSchema(BaseModel):
    count: int
    items: list[T]
