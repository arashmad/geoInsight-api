from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class LandUseCompositionRequest(BaseModel):
    layer_id: UUID


class VectorAnalysisResultRead(BaseModel):
    id: UUID
    aoi_id: UUID
    layer_id: UUID
    analysis_type: str
    metrics: dict[str, Any]
    created_at: datetime
