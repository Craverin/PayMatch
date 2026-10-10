from typing import Sequence

from app.enums import Currency, ProviderStatus
from app.models import Payment
from app.repositories.payments import PaymentRepository
from app.schemas.responses.payment_response import PaymentResponse


class PaymentService:
    def __init__(self, session):
        self.repository = PaymentRepository(session)

    def get_list(
            self,
            external_order_ids: list[str] | None = None,
            provider_statuses: list[ProviderStatus] | None = None,
            currencies: list[Currency] | None = None,
            limit: int = 25,
            offset: int = 0
    ) -> list[PaymentResponse]:
        return _to_payment_responses(
            self.repository.get_list(
                external_order_ids,
                provider_statuses,
                currencies,
                limit,
                offset
            )
        )

    def get(self, payment_id: int) -> PaymentResponse | None:
        return _to_payment_response(
            self.repository.get_by_id(payment_id)
        )


def _to_payment_responses(payments: Sequence[Payment]) -> list[PaymentResponse]:
    payment_responses = []

    for payment in payments:
        payment_responses.append(_to_payment_response(payment))

    return payment_responses

def _to_payment_response(payment: Payment | None) -> PaymentResponse | None:
    if payment is None:
        return None

    return PaymentResponse(
        id=payment.id,
        external_id=payment.external_id,
        external_order_id=payment.external_order_id,
        amount_minor=payment.amount_minor,
        amount_received_minor=payment.amount_received_minor,
        currency=payment.currency,
        status=payment.provider_status,
        external_created_at=payment.external_created_at,
        last_changed_at=payment.last_changed_at,
        last_sync_run_id=payment.last_sync_run_id
    )
