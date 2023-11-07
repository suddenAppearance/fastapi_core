from typing import Callable

from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, Session


def get_engines(sync_url: str, async_url: str) -> tuple[Engine, AsyncEngine]:
    return create_engine(sync_url), create_async_engine(async_url)


def get_session_factories(
    sync_engine: Engine, async_engine: Engine
) -> tuple[Callable[[], Session], Callable[[], AsyncSession]]:
    return sessionmaker(bind=sync_engine, expire_on_commit=False), sessionmaker(
        bind=async_engine, expire_on_commit=False, class_=AsyncSession
    )