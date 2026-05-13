from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from geoinsight_api.db.models.vector_layer import VectorLayer


class VectorLayerRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        name: str,
        description: str | None,
        layer_type: str,
        source: str | None,
        srid: int,
        properties_schema: dict | None,
    ) -> VectorLayer:
        vector_layer = VectorLayer(
            name=name,
            description=description,
            layer_type=layer_type,
            source=source,
            srid=srid,
            properties_schema=properties_schema,
        )

        self.session.add(vector_layer)
        self.session.flush()

        return vector_layer

    def list(self) -> list[VectorLayer]:
        stmt = select(VectorLayer).order_by(VectorLayer.created_at.desc())
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, layer_id: UUID) -> VectorLayer | None:
        return self.session.get(VectorLayer, layer_id)

    def delete(self, vector_layer: VectorLayer) -> None:
        self.session.delete(vector_layer)
        self.session.flush()
