from pydantic import AnyUrl
from pydantic_settings import BaseSettings


class ClickhouseSettings(BaseSettings):
    CLICKHOUSE_TCP_URL: AnyUrl | None = None
    CLICKHOUSE_LOG_TABLE: str | None = None
