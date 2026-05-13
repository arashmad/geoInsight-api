from uuid import UUID

from sqlalchemy.orm import Session

from geoinsight_api.db.models.vector_layer import VectorLayer
from geoinsight_api.repositories.vector_layer_repository import VectorLayerRepository


class VectorLayerNotFoundError(Exception):
    pass


class VectorLayerService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = VectorLayerRepository(session=session)

    def create_vector_layer(
        self,
        *,
        name: str,
        description: str | None,
        layer_type: str,
        source: str | None,
        srid: int,
        properties_schema: dict | None,
    ) -> VectorLayer:
        vector_layer = self.repository.create(
            name=name,
            description=description,
            layer_type=layer_type,
            source=source,
            srid=srid,
            properties_schema=properties_schema,
        )

        self.session.commit()
        self.session.refresh(vector_layer)

        return vector_layer

    def list_vector_layers(self) -> list[VectorLayer]:
        return self.repository.list()

    def get_vector_layer(self, layer_id: UUID) -> VectorLayer:
        vector_layer = self.repository.get_by_id(layer_id)

        if vector_layer is None:
            raise VectorLayerNotFoundError

        return vector_layer

    def delete_vector_layer(self, layer_id: UUID) -> None:
        vector_layer = self.get_vector_layer(layer_id)

        self.repository.delete(vector_layer)
        self.session.commit()
