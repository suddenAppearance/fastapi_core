from typing import TypeVar, Annotated, Literal, Generic

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedRequestSchema(BaseModel):
    page: Annotated[int, Field(ge=1)]
    page_size: Annotated[int, Field(ge=1)]

    def to_limit_offset(self, mode: Literal["dict", "tuple"] = "dict") -> dict[str, int] | tuple[int, int]:
        limit = self.page_size
        offset = (self.page - 1) * self.page_size

        match mode:
            case "dict":
                return dict(limit=limit, offset=offset)
            case "tuple":
                return limit, offset


class PaginatedResponseSchema(BaseModel, Generic[T]):
    count: int
    items: list[T]
