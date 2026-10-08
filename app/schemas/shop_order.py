from pydantic import BaseModel, Field, AwareDatetime

from app.enums import Currency, OrderStatus, PaymentStatus


class ShopOrder(BaseModel):
    id: str
    total_minor: int = Field(ge=0)
    currency: Currency
    status: OrderStatus
    payment_status: PaymentStatus
    created_at: AwareDatetime
    updated_at: AwareDatetime

class ShopOrdersPage(BaseModel):
    data: list[ShopOrder]
    next_cursor: str | None
