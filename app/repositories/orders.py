from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Order
from app.models.order import Currency, OrderStatus, PaymentStatus


class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, order_id: int) -> Order | None:
        return self.session.get(Order, order_id)

    def get_by_external_id(self, external_id: str) -> Order | None:
        return self.session.scalars(
            select(Order).where(Order.external_id == external_id)
        ).one_or_none()

    def get_by_last_sync_run_id(self, last_sync_run_id: int) -> Sequence[Order]:
        return self.session.scalars(
            select(Order).where(Order.last_sync_run_id == last_sync_run_id)
        ).all()

    def get_by_currency(self, currency: Currency) -> Sequence[Order]:
        return self.session.scalars(
            select(Order).where(Order.currency == currency)
        ).all()

    def get_by_status(self, status: OrderStatus) -> Sequence[Order]:
        return self.session.scalars(
            select(Order).where(Order.order_status == status)
        ).all()

    def get_by_payment_status(self, payment_status: PaymentStatus) -> Sequence[Order]:
        return self.session.scalars(
            select(Order).where(Order.payment_status == payment_status)
        ).all()

    def get_all(self) -> Sequence[Order]:
        return self.session.scalars(select(Order)).all()

    def get_list(
            self,
            order_statuses: list[OrderStatus] | None = None,
            payment_statuses: list[PaymentStatus] | None = None,
            currencies: list[Currency] | None = None,
            limit: int = 25,
            offset: int = 0
    ) -> Sequence[Order]:
        statement = select(Order)

        if order_statuses is not None:
            statement = statement.where(Order.order_status.in_(order_statuses))

        if payment_statuses is not None:
            statement = statement.where(Order.payment_status.in_(payment_statuses))

        if currencies is not None:
            statement = statement.where(Order.currency.in_(currencies))

        statement = (
            statement
            .order_by(Order.external_updated_at.desc(), Order.id.desc())
            .limit(limit)
            .offset(offset)
        )

        return self.session.scalars(statement).all()

    def add(self, order: Order) -> None:
        self.session.add(order)