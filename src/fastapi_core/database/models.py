from datetime import datetime

from sqlalchemy import Column, BigInteger, DateTime, func


class SerialIDBase:
    """
    Base Mixin for serial id primary key
    """

    id = Column(BigInteger, primary_key=True)


class CreateUpdateTimestampBase:
    """
    Base Mixin for created_at, updated_at timestamps
    """

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ExtendedBase(SerialIDBase, CreateUpdateTimestampBase):
    """
    Shortcut mixin for SerialIDBase and CreateUpdateTimestampBase
    """
