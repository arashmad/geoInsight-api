import uuid

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from geoinsight_api.db.base import Base


class VectorAnalysisResult(Base):
    __tablename__ = "vector_analysis_results"

    __table_args__ = (
        Index("ix_vector_analysis_results_aoi_id", "aoi_id"),
        Index("ix_vector_analysis_results_layer_id", "layer_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    aoi_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("aois.id", ondelete="CASCADE"),
        nullable=False,
    )

    layer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vector_layers.id", ondelete="CASCADE"),
        nullable=False,
    )

    analysis_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    metrics: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
