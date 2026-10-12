from datetime import UTC, datetime

import httpx

from app.database import SessionFactory
from app.clients.shop import ShopClient
from app.clients.stripe import StripeClient
from app.config import SHOP_BASE_URL
from app.repositories.orders import OrderRepository
from app.models.order import Order
from app.models.payment import Payment
from app.config import HTTP_REQUEST_TIMEOUT, STRIPE_BASE_URL, STRIPE_API_KEY
from app.enums import SyncRunStatus
from app.repositories.payments import PaymentRepository
from app.repositories.sync_runs import SyncRunRepository
from app.services.issue import IssueService
from app.services.reconciliation import reconcile

shop_httpx_client = httpx.Client(base_url=SHOP_BASE_URL, timeout=HTTP_REQUEST_TIMEOUT)
stripe_httpx_client = httpx.Client(
    base_url=STRIPE_BASE_URL,
    auth=(STRIPE_API_KEY, ""),
    timeout=HTTP_REQUEST_TIMEOUT
)

def sync_orders(sync_run_id: int) -> int:
    shop_client = ShopClient(shop_httpx_client)
    external_orders = shop_client.get_orders()

    with SessionFactory.begin() as session:
        order_repository = OrderRepository(session)

        for external_order in external_orders:
            order = order_repository.get_by_external_id(external_order.id)

            if order is None:
                order_repository.add(Order(
                    external_id=external_order.id,
                    amount_minor=external_order.total_minor,
                    currency=external_order.currency,
                    order_status=external_order.status,
                    payment_status=external_order.payment_status,
                    external_created_at=external_order.created_at,
                    external_updated_at=external_order.updated_at,
                    last_sync_run_id=sync_run_id
                ))

            else:
                order.amount_minor = external_order.total_minor
                order.order_status = external_order.status
                order.payment_status = external_order.payment_status
                order.external_updated_at = external_order.updated_at
                order.last_sync_run_id = sync_run_id

        return len(external_orders)


def sync_payments(sync_run_id: int) -> int:
    stripe_client = StripeClient(stripe_httpx_client)
    stripe_payments = stripe_client.get_payments()

    with SessionFactory.begin() as session:
        stripe_repository = PaymentRepository(session)

        for stripe_payment in stripe_payments:
            payment = stripe_repository.get_by_external_id(stripe_payment.id)

            if payment is None:
                stripe_repository.add(Payment(
                    external_id=stripe_payment.id,
                    external_order_id=stripe_payment.metadata.order_id,
                    amount_minor=stripe_payment.amount,
                    amount_received_minor=stripe_payment.amount_received,
                    currency=stripe_payment.currency,
                    provider_status=stripe_payment.status,
                    capture_method=stripe_payment.capture_method,
                    external_created_at=stripe_payment.created,
                    last_sync_run_id=sync_run_id
                ))

            else:
                payment.amount_received_minor = stripe_payment.amount_received
                payment.provider_status = stripe_payment.status
                payment.last_sync_run_id = sync_run_id

        return len(stripe_payments)

def run_sync(sync_run_id: int) -> None:
    orders_imported, payments_imported = 0, 0
    stage = "order import"

    try:
        orders_imported = sync_orders(sync_run_id)
        stage = "payments import"

        payments_imported = sync_payments(sync_run_id)

        stage = "reconciliation"
        issues = reconcile(sync_run_id)

        stage = "saving reconciliation results"

        with SessionFactory.begin() as session:
            repository = SyncRunRepository(session)
            sync_run = repository.get_by_id(sync_run_id)

            if sync_run is None:
                raise LookupError(f"Sync run {sync_run_id} was not found.")

            IssueService(session).apply_reconciliation(issues)

            sync_run.finished_at = datetime.now(UTC)
            sync_run.orders_imported = orders_imported
            sync_run.payments_imported = payments_imported
            sync_run.status = SyncRunStatus.SUCCEEDED

    except Exception as error:
        error_message = f"Failed during {stage}.\n{get_error_details(error)}"

        with SessionFactory.begin() as session:
            repository = SyncRunRepository(session)
            sync_run = repository.get_by_id(sync_run_id)

            if sync_run is not None:
                sync_run.finished_at = datetime.now(UTC)
                sync_run.status = SyncRunStatus.FAILED
                sync_run.orders_imported = orders_imported
                sync_run.payments_imported = payments_imported
                sync_run.error_message = error_message

        raise

def get_error_details(error: Exception) -> str:
    if isinstance(error, httpx.HTTPStatusError):
        return (
            f"HTTP status: {error.response.status_code}.\n"
            f"Response body: {error.response.text}"
        )

    elif isinstance(error, httpx.TimeoutException):
        return f"Request timed out ({type(error).__name__})."

    elif isinstance(error, httpx.ConnectError):
        return (
            f"Failed to connect to {error.request.url}.\n"
            f"Details: {error}"
        )

    elif isinstance(error, httpx.RequestError):
        return f"Request failed ({type(error).__name__}): {error}"

    else:
        return f"{type(error).__name__}: {error}"
