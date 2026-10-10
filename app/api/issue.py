from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Query, Depends
from sqlalchemy.orm import Session

from app.api.dependecies import get_issue_service, get_session
from app.enums import IssueStatus
from app.schemas.detected_issue import IssueType
from app.schemas.exceptions.issue_not_found import IssueNotFoundError
from app.schemas.exceptions.invalid_issue_status import InvalidIssueStatusError
from app.schemas.requests.issue_update import IssueUpdate
from app.schemas.responses.issue_response import IssueResponse
from app.services.issue import IssueService

router = APIRouter(prefix="/issues", tags=["Issue"])

@router.get("")
def get_issues(
        service: Annotated[IssueService, Depends(get_issue_service)],
        statuses: Annotated[list[IssueStatus] | None, Query(alias="status")] = None,
        types: Annotated[list[IssueType] | None, Query(alias="type")] = None,
        limit: Annotated[int, Query(ge=1, le=100)] = 25,
        offset: Annotated[int, Query(ge=0)] = 0
) -> list[IssueResponse]:
    return service.get_list(statuses, types, limit, offset)

@router.get("/{issue_id}")
def get_issue(
        service: Annotated[IssueService, Depends(get_issue_service)],
        issue_id: int
) -> IssueResponse:
    issue = service.get(issue_id)

    if issue is None:
        raise HTTPException(status_code=404, detail=f"Issue {issue_id} not found")

    return issue

@router.patch("/{issue_id}")
def update_issue(
        session: Annotated[Session, Depends(get_session)],
        issue_id: int,
        data: IssueUpdate
) -> IssueResponse:
    try:
        with session.begin():
            service = IssueService(session)
            return service.update(issue_id, data.status)

    except IssueNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except InvalidIssueStatusError as error:
        raise HTTPException(status_code=409, detail=str(error))
