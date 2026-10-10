from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, status, HTTPException, Query
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.api.dependecies import get_session, get_sync_run_service
from app.enums import SyncRunStatus
from app.schemas.exceptions.sync_already_running import SyncAlreadyRunningError
from app.schemas.responses.sync_run_created_response import SyncRunCreatedResponse
from app.schemas.responses.sync_run_response import SyncRunResponse
from app.services.sync import run_sync
from app.services.sync_run import SyncRunService

router = APIRouter(prefix="/sync-runs", tags=["Sync"])


@router.get("")
def get_sync_runs(
        service: Annotated[SyncRunService, Depends(get_sync_run_service)],
        statuses: Annotated[list[SyncRunStatus] | None, Query(alias="status")] = None,
        limit: Annotated[int, Query(ge=1, le=100)] = 25,
        offset: Annotated[int, Query(ge=0)] = 0
) -> list[SyncRunResponse]:
    return service.get_list(statuses, limit, offset)


@router.get("/{sync_run_id}")
def get_sync_run(
        service: Annotated[SyncRunService, Depends(get_sync_run_service)],
        sync_run_id: int
) -> SyncRunResponse:
    sync_run = service.get(sync_run_id)

    if sync_run is None:
        raise HTTPException(status_code=404, detail=f"Sync run {sync_run_id} not found")

    return sync_run


@router.post("", status_code=status.HTTP_202_ACCEPTED)
def synchronize(
        background_tasks: BackgroundTasks,
        session: Annotated[Session, Depends(get_session)]
) -> SyncRunCreatedResponse:
    with session.begin():
        try:
            response = SyncRunService(session).create()
        except SyncAlreadyRunningError as error:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))

    background_tasks.add_task(run_sync, response.id)

    return response

