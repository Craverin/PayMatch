from app.database import SessionFactory
from app.enums import ProviderStatus, OrderStatus, PaymentStatus
from app.models import Payment
from app.repositories.orders import OrderRepository
from app.repositories.payments import PaymentRepository
from app.schemas import detected_issue as issue_schema


def reconcile(sync_run_id: int) -> list[issue_schema.DetectedIssue]:
    issues: list[issue_schema.DetectedIssue] = []

    orders, payments = [], []

    with SessionFactory() as session:
        order_repository = OrderRepository(session)
        payment_repository = PaymentRepository(session)

        orders = order_repository.get_by_last_sync_run_id(sync_run_id)
        payments = payment_repository.get_by_last_sync_run_id(sync_run_id)


    orders_by_external_order_id = {
        order.external_id: order
        for order in orders
    }
    order_ids_with_successful_payments: set[str] = set()

    payments_by_order_id: dict[str, list[Payment]] = {}


    for payment in payments:
        if payment.external_order_id is not None:
            payments_by_order_id.setdefault(payment.external_order_id, []).append(payment)


    for payment in payments:
        if payment.provider_status != ProviderStatus.SUCCEEDED:
            continue

        if payment.external_order_id is None:
            issues.append(issue_schema.DetectedIssue(
                payment_id=payment.id,
                issue=issue_schema.MissingOrderReferenceIssue(
                    details=issue_schema.MissingOrderReferenceDetails(payment_id=payment.external_id)
                )
            ))
            continue

        order_ids_with_successful_payments.add(payment.external_order_id)

        order = orders_by_external_order_id.get(payment.external_order_id)

        if order is None:
            issues.append(issue_schema.DetectedIssue(
                payment_id=payment.id,
                issue=issue_schema.OrderNotFoundIssue(
                    details=issue_schema.OrderNotFoundDetails(
                        payment_id=payment.external_id,
                        order_id=payment.external_order_id
                    )
                )
            ))
            continue

        if order.order_status == OrderStatus.CANCELLED:
            issues.append(issue_schema.DetectedIssue(
                order_id=order.id,
                payment_id=payment.id,
                issue=issue_schema.PaymentForCancelledOrderIssue(
                    details=issue_schema.PaymentForCancelledOrderDetails(
                        order_id=order.external_id,
                        payment_id=payment.external_id
                    )
                )
            ))

        elif order.payment_status == PaymentStatus.UNPAID:
            issues.append(issue_schema.DetectedIssue(
                order_id=order.id,
                payment_id=payment.id,
                issue=issue_schema.OrderNotMarkedPaidIssue(
                    details=issue_schema.OrderNotMarkedPaidDetails(
                        order_id=order.external_id,
                        payment_id=payment.external_id
                    )
                )
            ))

        if payment.currency != order.currency:
            issues.append(issue_schema.DetectedIssue(
                order_id=order.id,
                payment_id=payment.id,
                issue=issue_schema.CurrencyMismatchIssue(
                    details=issue_schema.CurrencyMismatchDetails(
                        order_currency=order.currency,
                        payment_currency=payment.currency
                    )
                )
            ))

        elif payment.amount_received_minor != order.amount_minor:
            issues.append(issue_schema.DetectedIssue(
                order_id=order.id,
                payment_id=payment.id,
                issue=issue_schema.AmountMismatchIssue(
                    details=issue_schema.AmountMismatchDetails(
                        currency=payment.currency,
                        order_amount_minor=order.amount_minor,
                        payment_amount_received_minor=payment.amount_received_minor,
                        difference_minor=payment.amount_received_minor - order.amount_minor
                    )
                )
            ))

    for order_id in payments_by_order_id:
        successful_payments_ids = [
            payment.external_id
            for payment in payments_by_order_id[order_id]
            if payment.provider_status == ProviderStatus.SUCCEEDED
        ]

        if len(successful_payments_ids) > 1:
            issues.append(issue_schema.DetectedIssue(
                order_id=orders_by_external_order_id[order_id].id,
                issue=issue_schema.MultipleSuccessfulPaymentsIssue(
                    details=issue_schema.MultipleSuccessfulPaymentsDetails(
                        order_id=order_id,
                        payment_ids=successful_payments_ids
                    )
                )
            ))

    orders_without_successful_payment = [
        order
        for order in orders
        if order.payment_status == PaymentStatus.PAID
           and order.amount_minor > 0
           and order.external_id not in order_ids_with_successful_payments
    ]

    for order in orders_without_successful_payment:
        payments_ids = {
            payment.external_id: payment.provider_status
            for payment in payments_by_order_id.get(order.external_id, [])
        }

        issues.append(issue_schema.DetectedIssue(
            order_id=order.id,
            issue=issue_schema.PaidOrderWithoutSuccessfulPaymentIssue(
                details=issue_schema.PaidOrderWithoutSuccessfulPaymentDetails(
                    order_id=order.external_id,
                    payment_statuses=payments_ids
                )
            )
        ))

    return issues
