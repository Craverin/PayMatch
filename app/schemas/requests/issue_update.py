from typing import Literal

from pydantic import BaseModel

from app.enums import IssueStatus


class IssueUpdate(BaseModel):
    status: Literal[IssueStatus.OPEN, IssueStatus.IGNORED]
