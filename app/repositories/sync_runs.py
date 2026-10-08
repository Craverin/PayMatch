from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import SyncRun
from app.models.sync_run import SyncRunStatus


class SyncRunRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, sync_run_id: int) -> SyncRun | None:
        return self.session.get(SyncRun, sync_run_id)

    def get_by_status(self, sync_status: SyncRunStatus) -> Sequence[SyncRun]:
        return self.session.scalars(
            select(SyncRun).where(SyncRun.status == sync_status)
        ).all()

    def get_all(self) -> Sequence[SyncRun]:
        return self.session.scalars(select(SyncRun)).all()

    def get_list(
            self,
            statuses: list[SyncRunStatus] | None = None,
            limit: int = 25,
            offset: int = 0
    ) -> Sequence[SyncRun]:
        statement = select(SyncRun)

        if statuses is not None:
            statement = statement.where(SyncRun.status.in_(statuses))

        statement = (
            statement
            .order_by(SyncRun.started_at.desc(), SyncRun.id.desc())
            .limit(limit)
            .offset(offset)
        )

        return self.session.scalars(statement).all()

    def add(self, sync_run: SyncRun) -> None:
        self.session.add(sync_run)
