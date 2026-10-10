from datetime import datetime

from pydantic import BaseModel

from app.enums import Currency, ProviderStatus


class PaymentResponse(BaseModel):
    id: int
    external_id: str
    external_order_id: str | None
    amount_minor: int
    amount_received_minor: int
    currency: Currency
    status: ProviderStatus
    external_created_at: datetime
    last_changed_at: datetime
    last_sync_run_id: int
