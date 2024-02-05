import base64
from typing import TypeVar, Annotated, Literal, Generic, Any

from pydantic import BaseModel, Field, TypeAdapter

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


class TokenPaginatedRequestSchema(BaseModel):
    page_token: str | None
    page_size: Annotated[int, Field(ge=1)]


class TokenPaginatedResponseSchema(BaseModel, Generic[T]):
    next_page_token: str | None
    items: list[T]


class TokenPaginationItem(BaseModel):
    key: str
    operation: Literal[">", "<"]
    value: Any

    def get_condition_for_model(self, model: Any) -> Any:
        match self.operation:
            case ">":
                return getattr(model, self.key) > self.value
            case "<":
                return getattr(model, self.key) < self.value
            case ">=":
                return getattr(model, self.key) >= self.value
            case "<=":
                return getattr(model, self.key) <= self.value
            case _:
                raise ValueError(f"Unrecognized operator: {self.operator}")


items_list_type = TypeAdapter(list[TokenPaginationItem])


def token_loads(page_token: str | None) -> list[TokenPaginationItem]:
    if not page_token:
        return []

    return items_list_type.validate_json(base64.b64decode(page_token))


def token_dumps(items: list[TokenPaginationItem] | None) -> str | None:
    if not items:
        return None

    return base64.b64encode(items_list_type.dump_json(items)).decode()
