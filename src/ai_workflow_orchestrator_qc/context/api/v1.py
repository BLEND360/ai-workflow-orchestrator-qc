from fastapi import APIRouter, HTTPException
from ..schemas.models import ContextBuildRequest, ContextResponse

from ..core.time_window import resolve_time_windows
from ..core.normalizer import normalize_maintenance, normalize_operator_notes
from ..core.assembler import assemble_context

from ..repositories.maintenance_repo import MockMaintenanceRepository
from ..repositories.operator_notes_repo import MockOperatorNotesRepository
from ..repositories.metadata_repo import MockMetadataRepository
from ..config import Config

router = APIRouter()

maintenance_repo = MockMaintenanceRepository()
operator_notes_repo = MockOperatorNotesRepository()
metadata_repo = MockMetadataRepository()


@router.post("/context/build", response_model=ContextResponse)
def build_context(request: ContextBuildRequest):

    try:
        time_windows = resolve_time_windows(request.event_timestamp)

        metadata = metadata_repo.fetch(request.object.id)

        maintenance_raw = maintenance_repo.fetch(
            request.object.id,
            time_windows["maintenance"],
            Config.MAX_MAINTENANCE_RECORDS
        )

        operator_notes_raw = operator_notes_repo.fetch(
            request.object.id,
            time_windows["operator_notes"],
            Config.MAX_OPERATOR_NOTES
        )

        maintenance = normalize_maintenance(maintenance_raw)
        operator_notes = normalize_operator_notes(operator_notes_raw)

        context = assemble_context(
            request,
            maintenance,
            operator_notes,
            metadata,
            time_windows
        )

        return {"status": "success", "context": context}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Context build failed")
