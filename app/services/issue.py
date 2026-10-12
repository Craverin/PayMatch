from datetime import datetime, UTC
from typing import Sequence, Literal

from sqlalchemy.orm import Session

from app.enums import IssueStatus
from app.models import Issue
from app.repositories.issues import IssueRepository
from app.schemas.detected_issue import DetectedIssue, IssueType
from app.schemas.exceptions.issue_not_found import IssueNotFoundError
from app.schemas.exceptions.invalid_issue_status import InvalidIssueStatusError
from app.schemas.responses.issue_response import IssueResponse


class IssueService:
    def __init__(self, session: Session):
        self.repository = IssueRepository(session)

    def get_list(
            self,
            statuses: list[IssueStatus] | None = None,
            types: list[IssueType] | None = None,
            limit: int | None = 25,
            offset: int | None = 0
    ) -> list[IssueResponse]:
        return _to_issue_responses(
            self.repository.get_list(
                statuses,
                types,
                limit if limit is not None else 25,
                offset if offset is not None else 0
            )
        )

    def get(self, issue_id: int) -> IssueResponse | None:
        return _to_issue_response(self.repository.get_by_id(issue_id))

    def update(self,
               issue_id: int,
               status: Literal[IssueStatus.OPEN, IssueStatus.IGNORED]
   ) -> IssueResponse:
        issue = self.repository.get_by_id(issue_id)

        if issue is None:
            raise IssueNotFoundError(f"Issue {issue_id} was not found.")

        if issue.status == IssueStatus.RESOLVED:
            raise InvalidIssueStatusError("Resolved issues cannot be changed manually.")

        issue.status = status
        issue.updated_at = datetime.now()

        return _to_issue_response(issue)

    def apply_reconciliation(self, detected_issues: list[DetectedIssue]) -> None:
        open_issues = list(self.repository.get_by_status(IssueStatus.OPEN))
        open_issues_by_id = {issue.id: issue for issue in open_issues}

        for detected_issue in detected_issues:
            issue = self.repository.get(
                detected_issue.order_id,
                detected_issue.payment_id,
                detected_issue.issue.type
            )

            if issue is None:
                self.repository.add(Issue(
                    order_id=detected_issue.order_id,
                    payment_id=detected_issue.payment_id,
                    code=detected_issue.issue.type,
                    details=detected_issue.issue.details.model_dump(mode="json")
                ))

                continue

            if issue.status == IssueStatus.OPEN:
                new_details = detected_issue.issue.details.model_dump(mode="json")

                if issue.details != new_details:
                    issue.details = new_details
                    issue.updated_at = datetime.now(UTC)

                open_issues_by_id.pop(issue.id)

            elif issue.status == IssueStatus.RESOLVED:
                issue.status = IssueStatus.OPEN
                issue.resolved_at = None
                issue.updated_at = datetime.now(UTC)
                issue.details = detected_issue.issue.details.model_dump(mode="json")

            elif issue.status == IssueStatus.IGNORED:
                new_details = detected_issue.issue.details.model_dump(mode="json")

                if issue.details != new_details:
                    issue.details = new_details
                    issue.updated_at = datetime.now(UTC)

        for issue in open_issues_by_id.values():
            issue.status = IssueStatus.RESOLVED
            issue.updated_at = issue.resolved_at = datetime.now(UTC)


def _to_issue_responses(issues: Sequence[Issue]) -> list[IssueResponse]:
    issue_responses = []

    for issue in issues:
        issue_responses.append(_to_issue_response(issue))

    return issue_responses

def _to_issue_response(issue: Issue | None) -> IssueResponse | None:
    if issue is None:
        return None

    return IssueResponse.model_validate({
        "id": issue.id,
        "order_id": issue.order_id,
        "payment_id": issue.payment_id,
        "status": issue.status,
        "issue": {
            "type": issue.code,
            "details": issue.details
        },
        "created_at": issue.created_at,
        "updated_at": issue.updated_at,
        "resolved_at": issue.resolved_at
    })
