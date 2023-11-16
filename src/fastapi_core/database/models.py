from datetime import datetime

from sqlalchemy import Column, BigInteger, DateTime, func
from sqlalchemy.orm import Mapped


class SerialIDBase:
    """
    Base Mixin for serial id primary key
    """

    id: Mapped[int] = Column(BigInteger, primary_key=True)


class CreateUpdateTimestampBase:
    """
    Base Mixin for created_at, updated_at timestamps
    """

    created_at: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ExtendedBase(SerialIDBase, CreateUpdateTimestampBase):
    """
    Shortcut mixin for SerialIDBase and CreateUpdateTimestampBase
    """
