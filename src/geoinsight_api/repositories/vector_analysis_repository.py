from typing import Any
from uuid import UUID

from geoalchemy2 import Geography
from sqlalchemy import cast, func, select
from sqlalchemy.orm import Session

from geoinsight_api.db.models.aoi import AOI
from geoinsight_api.db.models.vector_analysis_result import VectorAnalysisResult
from geoinsight_api.db.models.vector_feature import VectorFeature


class VectorAnalysisRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def calculate_land_use_composition(
        self,
        *,
        aoi: AOI,
        layer_id: UUID,
    ) -> list[dict[str, Any]]:
        land_use_class = VectorFeature.properties["class"].astext.label("class_name")

        intersection_area_m2 = func.sum(
            func.ST_Area(
                cast(
                    func.ST_Intersection(AOI.geometry, VectorFeature.geometry),
                    Geography,
                )
            )
        ).label("area_m2")

        stmt = (
            select(
                land_use_class,
                intersection_area_m2,
            )
            .select_from(VectorFeature)
            .join(AOI, AOI.id == aoi.id)
            .where(VectorFeature.layer_id == layer_id)
            .where(func.ST_Intersects(AOI.geometry, VectorFeature.geometry))
            .group_by(land_use_class)
            .order_by(land_use_class)
        )

        rows = self.session.execute(stmt).all()

        results: list[dict[str, Any]] = []

        # TODO Check this block again -> it smells
        for row in rows:
            area_m2 = float(row.area_m2 or 0)

            if row.class_name is None:
                continue

            if area_m2 <= 0:
                continue

            results.append(
                {
                    "class": row.class_name,
                    "area_m2": area_m2,
                }
            )

        return results

    def create_result(
        self,
        *,
        aoi_id: UUID,
        layer_id: UUID,
        analysis_type: str,
        metrics: dict[str, Any],
    ) -> VectorAnalysisResult:
        result = VectorAnalysisResult(
            aoi_id=aoi_id,
            layer_id=layer_id,
            analysis_type=analysis_type,
            metrics=metrics,
        )

        self.session.add(result)
        self.session.flush()

        return result
