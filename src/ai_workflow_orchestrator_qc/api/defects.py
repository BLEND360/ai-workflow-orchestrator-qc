"""Defect events ingestion API endpoints."""

from datetime import datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status

from ai_workflow_orchestrator_qc.api.models import (
    IngestionAcknowledgment,
    QualityDefectEvent,
)
from ai_workflow_orchestrator_qc.core.idempotency import get_idempotency_store

router = APIRouter(prefix="/api/v1/defects", tags=["defects"])


@router.post(
    "/ingest",
    response_model=IngestionAcknowledgment,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a quality defect event",
    description="""
    Ingests a quality defect event with the following features:
    - Schema validation using Pydantic models
    - Automatic idempotency/duplicate detection based on event_id
    - Correlation ID generation for tracking
    - Returns acknowledgment with ingestion status
    """,
)
async def ingest_defect_event(
    event: QualityDefectEvent,
) -> IngestionAcknowledgment:
    """
    Ingest a quality defect event.

    This endpoint:
    1. Validates the event schema
    2. Checks for duplicate events (idempotency)
    3. Generates a correlation ID
    4. Returns an acknowledgment

    Args:
        event: The quality defect event to ingest

    Returns:
        IngestionAcknowledgment with correlation ID and status

    Raises:
        HTTPException: If there's an error processing the event
    """
    try:
        # Generate correlation ID
        correlation_id = uuid4()

        # Check for duplicate event (idempotency)
        idempotency_store = get_idempotency_store()
        is_duplicate, stored_correlation_id, stored_timestamp = (
            await idempotency_store.check_and_store(
                event.event_id, correlation_id
            )
        )

        # If duplicate, return acknowledgment with original correlation ID
        if is_duplicate:
            return IngestionAcknowledgment(
                correlation_id=stored_correlation_id,
                event_id=event.event_id,
                status="duplicate",
                ingested_at=stored_timestamp,
                message=f"Event with ID '{event.event_id}' was already ingested. "
                f"Original correlation ID: {stored_correlation_id}",
            )

        # New event ingested successfully
        ingested_at = datetime.utcnow()

        # Here you could add additional processing:
        # - Store to database
        # - Publish to message queue
        # - Trigger workflow orchestration
        # - etc.

        return IngestionAcknowledgment(
            correlation_id=correlation_id,
            event_id=event.event_id,
            status="accepted",
            ingested_at=ingested_at,
            message="Defect event successfully ingested",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing defect event: {str(e)}",
        ) from e

