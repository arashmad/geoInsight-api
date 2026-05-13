from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VectorLayerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    layer_type: str = Field(min_length=1, max_length=50)
    source: str | None = Field(default=None, max_length=255)
    srid: int = 4326
    properties_schema: dict[str, Any] | None = None


class VectorLayerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    layer_type: str
    source: str | None
    srid: int
    properties_schema: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime
