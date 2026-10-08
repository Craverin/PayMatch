from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Payment
from app.enums import ProviderStatus, Currency


class PaymentRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, payment_id: int) -> Payment | None:
        return self.session.get(Payment, payment_id)

    def get_by_external_id(self, external_payment_id: str) -> Payment | None:
        return self.session.scalars(
            select(Payment).where(Payment.external_id == external_payment_id)
        ).one_or_none()

    def get_by_external_order_id(self, external_order_id: str) -> Sequence[Payment]:
        return self.session.scalars(
            select(Payment).where(Payment.external_order_id == external_order_id)
        ).all()

    def get_by_last_sync_run_id(self, last_sync_run_id: int) -> Sequence[Payment]:
        return self.session.scalars(
            select(Payment).where(Payment.last_sync_run_id == last_sync_run_id)
        ).all()

    def get_unfinished(self) -> Sequence[Payment]:
        return self.session.scalars(
            select(Payment).where(
                Payment.provider_status.not_in(["canceled", "succeeded"])
            )
        ).all()

    def get_cancelled(self) -> Sequence[Payment]:
        return self.session.scalars(
            select(Payment).where(Payment.provider_status == 'canceled')
        ).all()

    def get_succeeded(self) -> Sequence[Payment]:
        return self.session.scalars(
            select(Payment).where(Payment.provider_status == 'succeeded')
        ).all()

    def get_list(
            self,
            external_order_ids: list[str] | None = None,
            provider_statuses: list[ProviderStatus] | None = None,
            currencies: list[Currency] | None = None,
            limit: int = 25,
            offset: int = 0
    ) -> Sequence[Payment]:
        statement = select(Payment)

        if external_order_ids is not None:
            statement = statement.where(Payment.external_order_id.in_(external_order_ids))

        if provider_statuses is not None:
            statement = statement.where(Payment.provider_status.in_(provider_statuses))

        if currencies is not None:
            statement = statement.where(Payment.currency.in_(currencies))

        statement = (
            statement
            .order_by(Payment.last_changed_at.desc(), Payment.id.desc())
            .limit(limit)
            .offset(offset)
        )

        return self.session.scalars(statement).all()

    def add(self, payment: Payment) -> None:
        self.session.add(payment)
