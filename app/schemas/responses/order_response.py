from datetime import datetime

from pydantic import BaseModel

from app.enums import Currency, OrderStatus, PaymentStatus


class OrderResponse(BaseModel):
    id: int
    external_id: str
    amount_minor: int
    currency: Currency
    order_status: OrderStatus
    payment_status: PaymentStatus
    external_created_at: datetime
    external_updated_at: datetime
    last_sync_run_id: int
