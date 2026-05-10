from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from geoinsight_api.api.deps import get_db
from geoinsight_api.api.v1.schemas.aoi import AOICreate, AOIRead
from geoinsight_api.services.aoi_service import AOIService, ProjectNotFoundError
from geoinsight_api.services.geometry_service import (
    InvalidGeometryError,
    UnsupportedGeometryTypeError,
)

router = APIRouter(
    prefix="/projects/{project_id}/aois",
    tags=["aois"],
)


def get_aoi_service(session: Session = Depends(get_db)) -> AOIService:
    return AOIService(session)


@router.post(
    "",
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
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only Polygon and MultiPolygon geometries are supported",
        ) from None

    except InvalidGeometryError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid geometry: {exc.reason}",
        ) from None