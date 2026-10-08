from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Identity, Text, func, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.enums import Currency, ProviderStatus


class Payment(Base):
    __tablename__ = 'payments'

    __table_args__ = (
        CheckConstraint(
            "provider_status IN ("
            "'requires_payment_method', 'requires_confirmation', 'requires_action', "
            "'processing', 'requires_capture', 'canceled', 'succeeded'"
            ")",
            name='ck_payments_provider_status'
        ),
        CheckConstraint(
            "capture_method IN ('automatic', 'automatic_async', 'manual')",
            name='ck_payments_capture_method'
        )
    )

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

    external_order_id: Mapped[str | None] = mapped_column(
        Text,
        CheckConstraint("external_order_id IS NULL OR trim(external_order_id) <> ''")
    )

    amount_minor: Mapped[int] = mapped_column(
        BigInteger,
        CheckConstraint("amount_minor >= 0")
    )

    amount_received_minor: Mapped[int] = mapped_column(
        BigInteger,
        CheckConstraint("amount_received_minor >= 0")
    )

    currency: Mapped[Currency] = mapped_column(
        Enum(Currency, native_enum=False),
        CheckConstraint("currency IN ('EUR', 'USD')")
    )

    provider_status: Mapped[ProviderStatus] = mapped_column(
        Enum(
            ProviderStatus,
            native_enum=False,
            values_callable=lambda enum: [item.value for item in enum]
         )
    )

    capture_method: Mapped[str] = mapped_column(Text)

    external_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    last_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    last_sync_run_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("sync_runs.id")
    )
