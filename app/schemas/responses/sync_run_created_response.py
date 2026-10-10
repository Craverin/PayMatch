from typing import Literal

from pydantic import BaseModel

from app.enums import SyncRunStatus


class SyncRunCreatedResponse(BaseModel):
    id: int
    status: Literal[SyncRunStatus.RUNNING] = SyncRunStatus.RUNNING
