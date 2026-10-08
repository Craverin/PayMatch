from datetime import datetime

from sqlalchemy import BigInteger, Identity, Text, CheckConstraint, DateTime, func, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.enums import Currency, OrderStatus, PaymentStatus
from app.models.base import Base


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True
    )

    external_id: Mapped[str] = mapped_column(
        Text,
        CheckConstraint("trim(external_id) <> ''"),
        unique=True
    )

    amount_minor: Mapped[int] = mapped_column(
        BigInteger,
        CheckConstraint("amount_minor >= 0")
    )

    currency: Mapped[Currency] = mapped_column(
        Enum(Currency, native_enum=False),
        CheckConstraint("currency IN ('EUR', 'USD')")
    )

    order_status: Mapped[OrderStatus] = mapped_column(
        Enum(
            OrderStatus,
            native_enum=False,
            values_callable=lambda enum: [item.value for item in enum]
        ),
        CheckConstraint("order_status IN ('open', 'cancelled')")
    )

    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(
            PaymentStatus,
            native_enum=False,
            values_callable = lambda enum: [item.value for item in enum]
        ),
        CheckConstraint("payment_status IN ('unpaid', 'paid')")
    )

    external_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    external_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    last_sync_run_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("sync_runs.id")
    )




