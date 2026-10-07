from enum import StrEnum


class IssueStatus(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"
    IGNORED = "ignored"


class Currency(StrEnum):
    USD = "USD"
    EUR = "EUR"


class OrderStatus(StrEnum):
    OPEN = "open"
    CANCELLED = "cancelled"


class PaymentStatus(StrEnum):
    PAID = "paid"
    UNPAID = "unpaid"


class SyncRunStatus(StrEnum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ProviderStatus(StrEnum):
    REQUIRES_PAYMENT_METHOD = "requires_payment_method"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    REQUIRES_ACTION = "requires_action"
    PROCESSING = "processing"
    REQUIRES_CAPTURE = "requires_capture"
    CANCELLED = "canceled"
    SUCCEEDED = "succeeded"