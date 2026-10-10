from collections.abc import Iterator
from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.database import SessionFactory
from app.services.issue import IssueService
from app.services.order import OrderService
from app.services.payment import PaymentService
from app.services.sync_run import SyncRunService


def get_session() -> Iterator[Session]:
    with SessionFactory() as session:
        yield session

def get_issue_service(session: Annotated[Session, Depends(get_session)]) -> IssueService:
    return IssueService(session)

def get_order_service(session: Annotated[Session, Depends(get_session)]) -> OrderService:
    return OrderService(session)

def get_payment_service(session: Annotated[Session, Depends(get_session)]) -> PaymentService:
    return PaymentService(session)

def get_sync_run_service(session: Annotated[Session, Depends(get_session)]) -> SyncRunService:
    return SyncRunService(session)
