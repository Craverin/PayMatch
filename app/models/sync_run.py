from datetime import datetime

from sqlalchemy import BigInteger, Identity, Text, CheckConstraint, DateTime, func, Integer, text, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.enums import SyncRunStatus
from app.models.base import Base


class SyncRun(Base):
    __tablename__ = 'sync_runs'

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True
    )

    status: Mapped[SyncRunStatus] = mapped_column(
        Enum(
            SyncRunStatus,
            native_enum=False,
            values_callable=lambda enum: [item.value for item in enum]
        ),
        CheckConstraint("status IN ('running', 'succeeded', 'failed')"),
        server_default=SyncRunStatus.RUNNING.value
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    orders_imported: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("orders_imported >= 0"),
        server_default=text("0")
    )

    payments_imported: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("payments_imported >= 0"),
        server_default=text("0")
    )

    error_message: Mapped[str | None] = mapped_column(Text)