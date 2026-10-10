from datetime import datetime

from pydantic import BaseModel

from app.enums import IssueStatus
from app.schemas.detected_issue import IssueType, ConcreteIssue


class IssueResponse(BaseModel):
    id: int
    order_id: int | None
    payment_id: int | None
    status: IssueStatus
    issue: ConcreteIssue
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None
