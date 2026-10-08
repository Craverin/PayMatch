from collections.abc import Sequence
from datetime import datetime, UTC

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Issue
from app.models.issue import IssueStatus
from app.schemas.detected_issue import IssueType


class IssueRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, order_id: int | None, payment_id: int | None, code: IssueType) -> Issue | None:
        return self.session.scalars(
            select(Issue).where(
                Issue.order_id == order_id,
                Issue.payment_id == payment_id,
                Issue.code == code
            )
        ).one_or_none()

    def get_by_id(self, issue_id: int) -> Issue | None:
        return self.session.get(Issue, issue_id)

    def get_by_order_id(self, order_id: int) -> Sequence[Issue]:
        return self.session.scalars(
            select(Issue).where(Issue.order_id == order_id)
        ).all()

    def get_by_payment_id(self, payment_id: int) -> Sequence[Issue]:
        return self.session.scalars(
            select(Issue).where(Issue.payment_id == payment_id)
        ).all()

    def get_by_status(self, status: IssueStatus) -> Sequence[Issue]:
        return self.session.scalars(
            select(Issue).where(Issue.status == status)
        ).all()

    def get_all(self) -> Sequence[Issue]:
        return self.session.scalars(select(Issue)).all()

    def get_list(
            self,
            statuses: list[IssueStatus] | None = None,
            types: list[IssueType] | None = None,
            limit: int = 25,
            offset: int = 0
    ) -> Sequence[Issue]:
        statement = select(Issue)

        if statuses is not None:
            statement = statement.where(Issue.status.in_(statuses))

        if types is not None:
            statement = statement.where(Issue.code.in_(types))

        statement = (
            statement
            .order_by(Issue.updated_at.desc(), Issue.id.desc())
            .limit(limit)
            .offset(offset)
        )

        return self.session.scalars(statement).all()

    def add(self, issue: Issue) -> None:
        self.session.add(issue)
