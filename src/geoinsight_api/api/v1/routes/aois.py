from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from geoinsight_api.db.session import get_db
from geoinsight_api.api.v1.schemas.aoi import AOICreate, AOIRead, AOIUpdate
from geoinsight_api.services.aoi_service import (
    AOINotFoundError,
    AOIService,
    ProjectNotFoundError)
from geoinsight_api.services.geometry_service import (
    InvalidGeometryError,
    UnsupportedGeometryTypeError,
)

router = APIRouter(tags=["aois"])


def get_aoi_service(session: Session = Depends(get_db)) -> AOIService:
    return AOIService(session)


@router.post(
    "/projects/{project_id}/aois",
    response_model=AOIRead,
    status_code=status.HTTP_201_CREATED,
)
def create_aoi(
    project_id: UUID,
    payload: AOICreate,
    service: AOIService = Depends(get_aoi_service),
) -> dict:
    try:
        aoi = service.create_aoi(
            project_id=project_id,
            name=payload.name,
            geometry=payload.geometry,
        )

        return service.to_response(aoi)

    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from None

    except UnsupportedGeometryTypeError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Only Polygon and MultiPolygon geometries are supported",
        ) from None

    except InvalidGeometryError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Invalid geometry: {exc.reason}",
        ) from None

@router.get(
    "/projects/{project_id}/aois",
    response_model=list[AOIRead],
)
def list_aois_by_project(
    project_id: UUID,
    service: AOIService = Depends(get_aoi_service),
) -> list[dict]:
    try:
        aois = service.list_aois_by_project(project_id)
        return [service.to_response(aoi) for aoi in aois]

    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from None


@router.get(
    "/aois/{aoi_id}",
    response_model=AOIRead,
)
def get_aoi(
    aoi_id: UUID,
    service: AOIService = Depends(get_aoi_service),
) -> dict:
    try:
        # TODO: Guard AOI serialization against nullable spatial fields
        aoi = service.get_aoi(aoi_id)
        return service.to_response(aoi)

    except AOINotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AOI not found",
        ) from None


@router.patch(
    "/aois/{aoi_id}",
    response_model=AOIRead,
)
def update_aoi(
    aoi_id: UUID,
    payload: AOIUpdate,
    service: AOIService = Depends(get_aoi_service),
) -> dict:
    update_data = payload.model_dump(exclude_unset=True)

    try:
        aoi = service.update_aoi(aoi_id, update_data)
        return service.to_response(aoi)

    except AOINotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AOI not found",
        ) from None

    except UnsupportedGeometryTypeError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Only Polygon and MultiPolygon geometries are supported",
        ) from None

    except InvalidGeometryError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Invalid geometry: {exc.reason}",
        ) from None


@router.delete(
    "/aois/{aoi_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_aoi(
    aoi_id: UUID,
    service: AOIService = Depends(get_aoi_service),
) -> None:
    try:
        service.delete_aoi(aoi_id)

    except AOINotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AOI not found",
        ) from None