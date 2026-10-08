from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Identity, Text, UniqueConstraint, func, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.enums import IssueStatus
from app.models.base import Base
from app.schemas.detected_issue import IssueType


class Issue(Base):
    __tablename__ = 'issues'

    __table_args__ = (
        CheckConstraint(
            "order_id IS NOT NULL OR payment_id IS NOT NULL",
            name='ck_issues_has_subject'
        ),
        UniqueConstraint(
            'order_id',
            'payment_id',
            'code',
            name='uq_issues_order_payment_code',
            postgresql_nulls_not_distinct=True
        ),
        CheckConstraint(
            "(status = 'resolved' AND resolved_at IS NOT NULL) "
            "OR (status <> 'resolved' AND resolved_at IS NULL)",
            name='ck_issues_resolved_at'
        )
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True
    )

    order_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("orders.id")
    )

    payment_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("payments.id")
    )

    code: Mapped[IssueType] = mapped_column(
        Enum(
            IssueType,
            native_enum=False,
            values_callable=lambda enum: [item.value for item in enum]
        ),
        CheckConstraint("trim(code) <> ''")
    )

    status: Mapped[IssueStatus] = mapped_column(
        Enum(
            IssueStatus,
            native_enum=False,
            values_callable=lambda enum: [item.value for item in enum]
        ),
        CheckConstraint("status IN ('open', 'resolved', 'ignored')"),
        server_default=IssueStatus.OPEN.value
    )

    details: Mapped[dict[str, Any]] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
