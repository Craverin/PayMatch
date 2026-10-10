from typing import Sequence

from app.enums import OrderStatus, PaymentStatus, Currency
from app.models import Order
from app.repositories.orders import OrderRepository
from app.schemas.responses.order_response import OrderResponse


class OrderService:
    def __init__(self, session):
        self.repository = OrderRepository(session)

    def get_list(
            self,
            order_statuses: list[OrderStatus] | None = None,
            payment_statuses: list[PaymentStatus] | None = None,
            currencies: list[Currency] | None = None,
            limit: int = 25,
            offset: int = 0
    ) -> list[OrderResponse]:
        return _to_order_responses(
            self.repository.get_list(
                order_statuses,
                payment_statuses,
                currencies,
                limit,
                offset
            )
        )

    def get(self, order_id: int) -> OrderResponse | None:
        return _to_order_response(
            self.repository.get_by_id(order_id)
        )

def _to_order_responses(orders: Sequence[Order]) -> list[OrderResponse]:
    order_responses = []

    for order in orders:
        order_responses.append(_to_order_response(order))

    return order_responses

def _to_order_response(order: Order | None) -> OrderResponse | None:
    if order is None:
        return None

    return OrderResponse(
        id=order.id,
        external_id=order.external_id,
        amount_minor=order.amount_minor,
        currency=order.currency,
        order_status=order.order_status,
        payment_status=order.payment_status,
        external_created_at=order.external_created_at,
        external_updated_at=order.external_updated_at,
        last_sync_run_id=order.last_sync_run_id
    )
