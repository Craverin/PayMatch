from enum import StrEnum
from typing import Literal, Annotated

from pydantic import BaseModel, Field

from app.enums import Currency


class DetectedIssue(BaseModel):
    order_id: int | None = None
    payment_id: int | None = None
    issue: ConcreteIssue

class IssueType(StrEnum):
    MISSING_ORDER_REFERENCE = "MISSING_ORDER_REFERENCE"
    ORDER_NOT_FOUND = "ORDER_NOT_FOUND"
    MULTIPLE_SUCCESSFUL_PAYMENTS = "MULTIPLE_SUCCESSFUL_PAYMENTS"
    PAYMENT_FOR_CANCELLED_ORDER = "PAYMENT_FOR_CANCELLED_ORDER"
    CURRENCY_MISMATCH = "CURRENCY_MISMATCH"
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"
    ORDER_NOT_MARKED_PAID = "ORDER_NOT_MARKED_PAID"
    PAID_ORDER_WITHOUT_SUCCESSFUL_PAYMENT = "PAID_ORDER_WITHOUT_SUCCESSFUL_PAYMENT"

type ConcreteIssue = Annotated[
    MissingOrderReferenceIssue
    | OrderNotFoundIssue
    | MultipleSuccessfulPaymentsIssue
    | PaymentForCancelledOrderIssue
    | CurrencyMismatchIssue
    | AmountMismatchIssue
    | OrderNotMarkedPaidIssue
    | PaidOrderWithoutSuccessfulPaymentIssue,
    Field(discriminator="type")
]


class MissingOrderReferenceIssue(BaseModel):
    type: Literal[IssueType.MISSING_ORDER_REFERENCE] = IssueType.MISSING_ORDER_REFERENCE
    details: MissingOrderReferenceDetails


class OrderNotFoundIssue(BaseModel):
    type: Literal[IssueType.ORDER_NOT_FOUND] = IssueType.ORDER_NOT_FOUND
    details: OrderNotFoundDetails


class MultipleSuccessfulPaymentsIssue(BaseModel):
    type: Literal[IssueType.MULTIPLE_SUCCESSFUL_PAYMENTS] = IssueType.MULTIPLE_SUCCESSFUL_PAYMENTS
    details: MultipleSuccessfulPaymentsDetails


class PaymentForCancelledOrderIssue(BaseModel):
    type: Literal[IssueType.PAYMENT_FOR_CANCELLED_ORDER] = IssueType.PAYMENT_FOR_CANCELLED_ORDER
    details: PaymentForCancelledOrderDetails


class CurrencyMismatchIssue(BaseModel):
    type: Literal[IssueType.CURRENCY_MISMATCH] = IssueType.CURRENCY_MISMATCH
    details: CurrencyMismatchDetails


class AmountMismatchIssue(BaseModel):
    type: Literal[IssueType.AMOUNT_MISMATCH] = IssueType.AMOUNT_MISMATCH
    details: AmountMismatchDetails


class OrderNotMarkedPaidIssue(BaseModel):
    type: Literal[IssueType.ORDER_NOT_MARKED_PAID] = IssueType.ORDER_NOT_MARKED_PAID
    details: OrderNotMarkedPaidDetails


class PaidOrderWithoutSuccessfulPaymentIssue(BaseModel):
    type: Literal[IssueType.PAID_ORDER_WITHOUT_SUCCESSFUL_PAYMENT] = IssueType.PAID_ORDER_WITHOUT_SUCCESSFUL_PAYMENT
    details: PaidOrderWithoutSuccessfulPaymentDetails


class MissingOrderReferenceDetails(BaseModel):
    payment_id: str


class OrderNotFoundDetails(BaseModel):
    payment_id: str
    order_id: str


class MultipleSuccessfulPaymentsDetails(BaseModel):
    order_id: str
    payment_ids: list[str]


class PaymentForCancelledOrderDetails(BaseModel):
    order_id: str
    payment_id: str


class CurrencyMismatchDetails(BaseModel):
    order_currency: Currency
    payment_currency: Currency


class AmountMismatchDetails(BaseModel):
    currency: Currency
    order_amount_minor: int
    payment_amount_received_minor: int
    difference_minor: int


class OrderNotMarkedPaidDetails(BaseModel):
    order_id: str
    payment_id: str


class PaidOrderWithoutSuccessfulPaymentDetails(BaseModel):
    order_id: str
    payment_statuses: dict[str, str]
