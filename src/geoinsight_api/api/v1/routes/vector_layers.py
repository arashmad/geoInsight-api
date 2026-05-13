from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from geoinsight_api.api.v1.schemas.vector_layer import (
    VectorLayerCreate,
    VectorLayerRead,
)
from geoinsight_api.db.session import get_db
from geoinsight_api.services.vector_layer_service import (
    VectorLayerNotFoundError,
    VectorLayerService,
)

router = APIRouter(prefix="/vector-layers", tags=["vector-layers"])


def get_vector_layer_service(
    session: Session = Depends(get_db),
) -> VectorLayerService:
    return VectorLayerService(session=session)


@router.post(
    "",
    response_model=VectorLayerRead,
    status_code=status.HTTP_201_CREATED,
)
def create_vector_layer(
    payload: VectorLayerCreate,
    service: VectorLayerService = Depends(get_vector_layer_service),
) -> VectorLayerRead:
    return service.create_vector_layer(
        name=payload.name,
        description=payload.description,
        layer_type=payload.layer_type,
        source=payload.source,
        srid=payload.srid,
        properties_schema=payload.properties_schema,
    )


@router.get("", response_model=list[VectorLayerRead])
def list_vector_layers(
    service: VectorLayerService = Depends(get_vector_layer_service),
) -> list[VectorLayerRead]:
    return service.list_vector_layers()


@router.get("/{layer_id}", response_model=VectorLayerRead)
def get_vector_layer(
    layer_id: UUID,
    service: VectorLayerService = Depends(get_vector_layer_service),
) -> VectorLayerRead:
    try:
        return service.get_vector_layer(layer_id)
    except VectorLayerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vector layer not found",
        ) from None


@router.delete(
    "/{layer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_vector_layer(
    layer_id: UUID,
    service: VectorLayerService = Depends(get_vector_layer_service),
) -> None:
    try:
        service.delete_vector_layer(layer_id)
    except VectorLayerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vector layer not found",
        ) from None
