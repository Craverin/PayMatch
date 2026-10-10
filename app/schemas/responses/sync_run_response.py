from datetime import datetime

from pydantic import BaseModel

from app.enums import SyncRunStatus


class SyncRunResponse(BaseModel):
    id: int
    status: SyncRunStatus
    started_at: datetime
    finished_at: datetime | None
    orders_imported: int
    payments_imported: int
    error: str | None
