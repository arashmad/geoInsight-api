from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from geoinsight_api.db.models.aoi import AOI
from geoinsight_api.db.models.vector_analysis_result import VectorAnalysisResult
from geoinsight_api.db.models.vector_layer import VectorLayer
from geoinsight_api.repositories.vector_analysis_repository import (
    VectorAnalysisRepository,
)

LAND_USE_COMPOSITION = "land_use_composition"


class AOIForAnalysisNotFoundError(Exception):
    pass


class VectorAnalysisResultNotFound(Exception):
    pass


class VectorLayerForAnalysisNotFoundError(Exception):
    pass


class InvalidVectorLayerTypeError(Exception):
    pass


class VectorAnalysisService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = VectorAnalysisRepository(session=session)

    def get_result(self, result_id: UUID) -> VectorAnalysisResult:
        result = self.repository.get_result_by_id(result_id)

        if result is None:
            raise VectorAnalysisResultNotFound

        return result

    def get_results_for_aoi(self, aoi_id: UUID) -> list[VectorAnalysisResult]:
        aoi = self.session.get(AOI, aoi_id)

        if aoi is None:
            raise AOIForAnalysisNotFoundError

        return self.repository.list_results_by_aoi_id(aoi_id)

    def run_land_use_composition(
        self,
        *,
        aoi_id: UUID,
        layer_id: UUID,
    ) -> VectorAnalysisResult:
        aoi = self.session.get(AOI, aoi_id)

        if aoi is None:
            raise AOIForAnalysisNotFoundError

        layer = self.session.get(VectorLayer, layer_id)

        if layer is None:
            raise VectorLayerForAnalysisNotFoundError

        if layer.layer_type != "land_use":
            raise InvalidVectorLayerTypeError

        class_rows = self.repository.calculate_land_use_composition(
            aoi=aoi,
            layer_id=layer_id,
        )

        covered_area_m2 = self.repository.calculate_coverage_area_m2(
            aoi=aoi,
            layer_id=layer_id,
        )

        total_aoi_area_m2 = float(aoi.area_m2 or 0)

        classes = [
            {
                "class": row["class"],
                "area_m2": row["area_m2"],
                "percentage": self._calculate_percentage(
                    part_area_m2=row["area_m2"],
                    total_area_m2=total_aoi_area_m2,
                ),
            }
            for row in class_rows
        ]

        metrics: dict[str, Any] = {
            "total_aoi_area_m2": total_aoi_area_m2,
            "classes": classes,
            "covered_area_m2": round(covered_area_m2, 4),
            "covered_area_percentage": self._calculate_percentage(
                part_area_m2=covered_area_m2, total_area_m2=total_aoi_area_m2
            ),
        }

        result = self.repository.create_result(
            aoi_id=aoi_id,
            layer_id=layer_id,
            analysis_type=LAND_USE_COMPOSITION,
            metrics=metrics,
        )

        self.session.commit()
        self.session.refresh(result)

        return result

    @staticmethod
    def _calculate_percentage(
        *,
        part_area_m2: float,
        total_area_m2: float,
    ) -> float:
        if total_area_m2 <= 0:
            return 0.0

        return round((part_area_m2 / total_area_m2) * 100, 4)
