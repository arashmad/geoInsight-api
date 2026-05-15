from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from geoinsight_api.api.v1.schemas.vector_analysis import (
    LandUseCompositionRequest,
    VectorAnalysisResultRead,
)
from geoinsight_api.db.session import get_db
from geoinsight_api.services.vector_analysis_service import (
    AOIForAnalysisNotFoundError,
    InvalidVectorLayerTypeError,
    VectorAnalysisService,
    VectorLayerForAnalysisNotFoundError,
)

router = APIRouter(tags=["vector-analysis"])


def get_vector_analysis_service(
    session: Session = Depends(get_db),
) -> VectorAnalysisService:
    return VectorAnalysisService(session=session)


@router.post(
    "/aois/{aoi_id}/land-use-composition",
    response_model=VectorAnalysisResultRead,
    status_code=status.HTTP_201_CREATED,
)
def run_land_use_composition(
    aoi_id: UUID,
    payload: LandUseCompositionRequest,
    service: VectorAnalysisService = Depends(get_vector_analysis_service),
) -> VectorAnalysisResultRead:
    try:
        return service.run_land_use_composition(
            aoi_id=aoi_id,
            layer_id=payload.layer_id,
        )

    except AOIForAnalysisNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AOI not found",
        ) from None

    except VectorLayerForAnalysisNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vector layer not found",
        ) from None

    except InvalidVectorLayerTypeError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Vector layer must have layer_type='land_use'",
        ) from None
