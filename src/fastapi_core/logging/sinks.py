from __future__ import annotations

import loguru
from pydantic_core import Url

from fastapi_core.settings.app import APISettings


class ClickHouseSink:
    """
    Table DDL:

    CREATE TABLE <table_name>
    (
        service   varchar(64),
        timestamp DATETIME64(3, 'Europe/Moscow'),
        message   varchar,
        file      varchar,
        lineno    int,
        level     varchar,
        function  varchar
    )
        ENGINE MergeTree
            ORDER BY timestamp
            PARTITION BY toYYYYMM(timestamp);
    """

    def __init__(self, clickhouse_url: Url, table_name: str):
        from asynch.connection import Connection
        self.clickhouse_url = clickhouse_url
        self.table_name = table_name
        self._conn: Connection | None = None
        self.database = self.clickhouse_url.path.lstrip("/")

    async def conn(self):
        from asynch import connect
        if not self._conn:
            self._conn = await connect(
                host=self.clickhouse_url.host,
                port=self.clickhouse_url.port,
                database=self.clickhouse_url.path.lstrip("/"),
                user=self.clickhouse_url.username or "default",
                password=self.clickhouse_url.password or ""
            )
        return self._conn

    async def sink(self, message: loguru.Message):
        from asynch.cursors import DictCursor
        from asynch.errors import ClickHouseException

        conn = await self.conn()
        try:
            async with conn.cursor(cursor=DictCursor) as cursor:
                await cursor.execute(
                    f"INSERT INTO {self.database}.{self.table_name} "
                    f"(service, timestamp, message, file, lineno, level, function) VALUES ",
                    [
                        dict(
                            service=APISettings().SERVICE_NAME,
                            timestamp=message.record["time"],
                            message=message.record["message"],
                            file=message.record["file"].path,
                            lineno=message.record["line"],
                            level=message.record["level"].name,
                            function=message.record["function"]
                        )
                    ]
                )
        except ClickHouseException:
            ...
