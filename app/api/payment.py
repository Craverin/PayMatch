from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependecies import get_payment_service
from app.enums import Currency, ProviderStatus
from app.schemas.responses.payment_response import PaymentResponse
from app.services.payment import PaymentService


router = APIRouter(prefix="/payments", tags=["Payment"])


@router.get("")
def get_payments(
        service: Annotated[PaymentService, Depends(get_payment_service)],
        external_order_ids: Annotated[list[str] | None, Query(alias="external_order_id")] = None,
        provider_statuses: Annotated[list[ProviderStatus] | None, Query(alias="provider_status")] = None,
        currencies: Annotated[list[Currency] | None, Query(alias="currency")] = None,
        limit: Annotated[int, Query(ge=1, le=100)] = 25,
        offset: Annotated[int, Query(ge=0)] = 0
) -> list[PaymentResponse]:
    return service.get_list(external_order_ids, provider_statuses, currencies, limit, offset)


@router.get("/{payment_id}")
def get_payment(
        service: Annotated[PaymentService, Depends(get_payment_service)],
        payment_id: int
) -> PaymentResponse:
    payment = service.get(payment_id)

    if payment is None:
        raise HTTPException(status_code=404, detail=f"Payment {payment_id} not found")

    return payment
