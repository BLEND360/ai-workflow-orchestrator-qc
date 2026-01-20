from datetime import datetime
from ..config import Config


def assemble_context(
    request,
    maintenance,
    operator_notes,
    metadata,
    time_windows
):
    return {
        "context_version": Config.CONTEXT_VERSION,
        "correlation_id": request.correlation_id,
        "event": {
            "event_id": request.event_id,
            "machine_id": request.object.id,
            "defect_type": request.defect_type,
            "timestamp": request.event_timestamp.isoformat()
        },
        "maintenance_history": maintenance,
        "operator_notes": operator_notes,
        "machine_metadata": metadata,
        "time_windows": {
            k: {
                "from": v["from"].isoformat(),
                "to": v["to"].isoformat()
            } for k, v in time_windows.items()
        },
        "generated_at": datetime.utcnow().isoformat()
    }
