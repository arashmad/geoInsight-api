import uuid

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from geoinsight_api.db.base import Base


class VectorLayer(Base):
    __tablename__ = "vector_layers"

    # __table_args__ = (
    #     UniqueConstraint(
    #         "name",
    #         "layer_type",
    #         "source",
    #         name="uq_vector_layers_name_type_source",
    #     ),
    # )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    layer_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    source: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    srid: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=4326,
    )

    properties_schema: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
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

    features = relationship(
        "VectorFeature",
        back_populates="layer",
        cascade="all, delete-orphan",
    )
