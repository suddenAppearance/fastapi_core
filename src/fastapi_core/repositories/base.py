import abc
from typing import Generic, TypeVar, Iterable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import CompoundSelect, Delete, Select, Update

T = TypeVar("T")


class BaseRepository(abc.ABC, Generic[T]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def one_or_none(self, statement: Select | CompoundSelect) -> T | None:
        return (await self.session.execute(statement)).scalars().one_or_none()

    async def one(self, statement: Select | CompoundSelect) -> T:
        return (await self.session.execute(statement)).scalars().one()

    async def add_all(self, objs: list):
        self.session.add_all(objs)

    async def all(self, statement: Select | CompoundSelect) -> Iterable[T]:
        return (await self.session.execute(statement)).scalars().all()

    async def execute(self, statement: Select | Update | Delete):
        return await self.session.execute(statement)

    async def first(self, statement: Select | CompoundSelect) -> T | None:
        return (await self.session.execute(statement)).scalars().first()
