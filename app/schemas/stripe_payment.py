from pydantic import BaseModel, Field, AwareDatetime, BeforeValidator
from typing import Annotated

from app.enums import Currency
from app.enums import ProviderStatus


def normalize_currency(value: object) -> object:
    if isinstance(value, str):
        return value.upper()
    return value


class StripePaymentMetadata(BaseModel):
    order_id: str | None = None


class StripePayment(BaseModel):
    id: str
    object_type: str = Field(alias="object")
    amount: int = Field(ge=0)
    amount_received: int = Field(ge=0)
    currency: Annotated[Currency, BeforeValidator(normalize_currency)]
    status: ProviderStatus
    capture_method: str
    created: AwareDatetime
    metadata: StripePaymentMetadata


class StripePaymentPage(BaseModel):
    has_more: bool
    data: list[StripePayment]
