from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AOICreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    geometry: dict[str, Any]


class AOIRead(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    geometry: dict[str, Any]
    area_m2: float
    centroid: dict[str, Any]
    bbox: list[float]
    created_at: datetime
    updated_at: datetime