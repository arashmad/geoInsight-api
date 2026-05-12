import uuid

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from geoinsight_api.db.base import Base


class VectorFeature(Base):
    __tablename__ = "vector_features"

    __table_args__ = (
        Index(
            "ix_vector_features_geometry",
            "geometry",
            postgresql_using="gist",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    layer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vector_layers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    geometry: Mapped[object] = mapped_column(
        Geometry(
            geometry_type="MULTIPOLYGON",
            srid=4326,
            spatial_index=False,
        ),
        nullable=False,
    )

    properties: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    layer = relationship(
        "VectorLayer",
        back_populates="features",
    )
