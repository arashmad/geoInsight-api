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
    VectorAnalysisResultNotFound,
    VectorAnalysisService,
    VectorLayerForAnalysisNotFoundError,
)

router = APIRouter(tags=["vector-analysis"])


def get_vector_analysis_service(
    session: Session = Depends(get_db),
) -> VectorAnalysisService:
    return VectorAnalysisService(session=session)


@router.get(
    "/vector-analysis-results/{result_id}",
    response_model=VectorAnalysisResultRead,
    status_code=status.HTTP_200_OK,
)
def get_vector_analysis_result_by_id(
    result_id: UUID,
    service: VectorAnalysisService = Depends(get_vector_analysis_service),
) -> VectorAnalysisResultRead:
    try:
        return service.get_result(result_id=result_id)
    except VectorAnalysisResultNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vector analysis results not found",
        ) from None


@router.get(
    "/aois/{aoi_id}/vector-analysis-results",
    response_model=list[VectorAnalysisResultRead],
    status_code=status.HTTP_200_OK,
)
def get_vector_analysis_results_by_aoi(
    aoi_id: UUID, service: VectorAnalysisService = Depends(get_vector_analysis_service)
) -> list[VectorAnalysisResultRead]:
    try:
        return service.get_results_for_aoi(aoi_id=aoi_id)
    except AOIForAnalysisNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AOI not found",
        ) from None


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
