"""Idempotency service for duplicate event detection."""

import asyncio
from datetime import datetime
from typing import Dict, Optional, Tuple
from uuid import UUID

from ai_workflow_orchestrator_qc.api.models import QualityDefectEvent


class IdempotencyStore:
    """In-memory store for tracking ingested events (idempotency)."""

    def __init__(self):
        """Initialize the idempotency store."""
        self._store: Dict[str, Tuple[UUID, datetime]] = {}
        self._lock = asyncio.Lock()

    async def check_and_store(
        self, event_id: str, correlation_id: UUID
    ) -> Tuple[bool, Optional[UUID], Optional[datetime]]:
        """
        Check if an event ID already exists and store if new.

        Args:
            event_id: The unique event identifier
            correlation_id: The correlation ID for this ingestion request

        Returns:
            Tuple of (is_duplicate, existing_correlation_id, existing_timestamp)
            If not duplicate: (False, correlation_id, current_timestamp)
            If duplicate: (True, original_correlation_id, original_timestamp)
        """
        async with self._lock:
            if event_id in self._store:
                original_correlation_id, original_timestamp = self._store[event_id]
                return True, original_correlation_id, original_timestamp

            # Store new event
            timestamp = datetime.utcnow()
            self._store[event_id] = (correlation_id, timestamp)
            return False, correlation_id, timestamp

    async def get_event_info(
        self, event_id: str
    ) -> Optional[Tuple[UUID, datetime]]:
        """
        Get correlation ID and timestamp for an existing event.

        Args:
            event_id: The unique event identifier

        Returns:
            Tuple of (correlation_id, timestamp) if exists, None otherwise
        """
        async with self._lock:
            return self._store.get(event_id)


# Global singleton instance
_idempotency_store: Optional[IdempotencyStore] = None


def get_idempotency_store() -> IdempotencyStore:
    """
    Get the global idempotency store instance.

    Returns:
        The singleton IdempotencyStore instance
    """
    global _idempotency_store
    if _idempotency_store is None:
        _idempotency_store = IdempotencyStore()
    return _idempotency_store

