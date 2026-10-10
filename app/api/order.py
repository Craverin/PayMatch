from typing import Annotated

from fastapi import APIRouter, Query, HTTPException
from fastapi.params import Depends

from app.api.dependecies import get_order_service
from app.enums import OrderStatus, PaymentStatus, Currency
from app.schemas.responses.order_response import OrderResponse
from app.services.order import OrderService

router = APIRouter(prefix="/orders", tags=["Order"])

@router.get("")
def get_orders(
        service: Annotated[OrderService, Depends(get_order_service)],
        order_statuses: Annotated[list[OrderStatus] | None, Query(alias="order_status")] = None,
        payment_statuses: Annotated[list[PaymentStatus] | None, Query(alias="payment_status")] = None,
        currencies: Annotated[list[Currency] | None, Query(alias="currency")] = None,
        limit: Annotated[int, Query(ge=1, le=100)] = 25,
        offset: Annotated[int, Query(ge=0)] = 0
) -> list[OrderResponse]:
    return service.get_list(order_statuses, payment_statuses, currencies, limit, offset)

@router.get("/{order_id}")
def get_order(
        service: Annotated[OrderService, Depends(get_order_service)],
        order_id: int
) -> OrderResponse:
    order = service.get(order_id)

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return order
