from typing import Sequence

from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from app.database import SessionFactory
from app.enums import SyncRunStatus
from app.models import Payment, SyncRun
from app.repositories.sync_runs import SyncRunRepository
from app.schemas.exceptions.sync_already_running import SyncAlreadyRunningError
from app.schemas.responses.sync_run_response import SyncRunResponse
from app.schemas.responses.sync_run_created_response import SyncRunCreatedResponse


class SyncRunService:
    def __init__(self, session):
        self.session = session
        self.repository = SyncRunRepository(session)

    def get_all(self) -> list[SyncRunResponse]:
        return _to_sync_run_responses(self.repository.get_all())

    def get_list(
            self,
            statuses: list[SyncRunStatus] | None = None,
            limit: int = 25,
            offset: int = 0
    ) -> list[SyncRunResponse]:
        return _to_sync_run_responses(self.repository.get_list(statuses, limit, offset))

    def get(self, sync_run_id: int) -> SyncRunResponse | None:
        return _to_sync_run_response(self.repository.get_by_id(sync_run_id))

    def create(self) -> SyncRunCreatedResponse:
        sync_run = SyncRun()
        self.repository.add(sync_run)

        try:
            self.session.flush()
        except IntegrityError as error:
            if (
                isinstance(error.orig, UniqueViolation)
                and error.orig.diag.constraint_name == "uq_sync_runs_single_running"
            ):
                raise SyncAlreadyRunningError("A synchronization is already running.") from error

            raise

        return SyncRunCreatedResponse(id=sync_run.id)


def _to_sync_run_responses(sync_runs: Sequence[SyncRun]) -> list[SyncRunResponse]:
    runs = []

    for sync_run in sync_runs:
        runs.append(_to_sync_run_response(sync_run))

    return runs

def _to_sync_run_response(sync_run: SyncRun | None) -> SyncRunResponse | None:
    if sync_run is None:
        return None

    return SyncRunResponse(
        id=sync_run.id,
        status=sync_run.status,
        started_at=sync_run.started_at,
        finished_at=sync_run.finished_at,
        orders_imported=sync_run.orders_imported,
        payments_imported=sync_run.payments_imported,
        error=sync_run.error_message
    )
