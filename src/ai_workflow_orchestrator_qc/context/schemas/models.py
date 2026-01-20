from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any


class ObjectRef(BaseModel):
    type: str
    id: str


class ContextBuildRequest(BaseModel):
    event_id: str
    object: ObjectRef
    defect_type: str
    event_timestamp: datetime
    correlation_id: str


class ContextResponse(BaseModel):
    status: str
    context: Dict[str, Any]
