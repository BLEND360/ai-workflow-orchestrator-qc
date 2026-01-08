"""Pydantic models for API request/response schemas."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DefectSeverity(str, Enum):
    """Defect severity levels."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class DefectCategory(str, Enum):
    """Defect category types."""

    FUNCTIONAL = "FUNCTIONAL"
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"
    USABILITY = "USABILITY"
    COMPATIBILITY = "COMPATIBILITY"
    DATA_QUALITY = "DATA_QUALITY"
    OTHER = "OTHER"


class QualityDefectEvent(BaseModel):
    """Schema for quality defect event ingestion."""

    event_id: str = Field(
        ...,
        description="Unique identifier for the defect event (used for idempotency)",
        min_length=1,
        max_length=255,
    )
    defect_type: str = Field(
        ...,
        description="Type/category of the defect",
        min_length=1,
        max_length=100,
    )
    severity: DefectSeverity = Field(
        ...,
        description="Severity level of the defect",
    )
    category: DefectCategory = Field(
        ...,
        description="Category of the defect",
    )
    description: str = Field(
        ...,
        description="Detailed description of the defect",
        min_length=1,
        max_length=5000,
    )
    component: str = Field(
        ...,
        description="Component/system where the defect was found",
        min_length=1,
        max_length=200,
    )
    detected_at: datetime = Field(
        ...,
        description="Timestamp when the defect was detected",
    )
    detected_by: Optional[str] = Field(
        None,
        description="Identifier of the person/system that detected the defect",
        max_length=200,
    )
    metadata: Optional[dict] = Field(
        None,
        description="Additional metadata about the defect",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "event_id": "defect-2024-001",
                "defect_type": "Data Validation Error",
                "severity": "HIGH",
                "category": "DATA_QUALITY",
                "description": "Invalid data format detected in customer records",
                "component": "data-ingestion-service",
                "detected_at": "2024-01-15T10:30:00Z",
                "detected_by": "automated-test-suite",
                "metadata": {
                    "test_case": "TC-123",
                    "environment": "staging",
                },
            }
        }


class IngestionAcknowledgment(BaseModel):
    """Response schema for defect event ingestion acknowledgment."""

    correlation_id: UUID = Field(
        ...,
        description="Unique correlation ID generated for this ingestion request",
    )
    event_id: str = Field(
        ...,
        description="The event ID that was ingested",
    )
    status: str = Field(
        ...,
        description="Ingestion status (accepted or duplicate)",
    )
    ingested_at: datetime = Field(
        ...,
        description="Timestamp when the event was ingested",
    )
    message: str = Field(
        ...,
        description="Human-readable message about the ingestion result",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
                "event_id": "defect-2024-001",
                "status": "accepted",
                "ingested_at": "2024-01-15T10:30:00.123456Z",
                "message": "Defect event successfully ingested",
            }
        }

