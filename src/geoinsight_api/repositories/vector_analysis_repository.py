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

    def get_result_by_id(self, result_id: UUID) -> VectorAnalysisResult | None:
        """Find results by id."""
        return self.session.get(VectorAnalysisResult, result_id)

    def list_results_by_aoi_id(self, aoi_id: UUID) -> list[VectorAnalysisResult] | None:
        """Find all results belong to a specific aoi."""
        stmt = (
            select(VectorAnalysisResult)
            .where(VectorAnalysisResult.aoi_id == aoi_id)
            .order_by(VectorAnalysisResult.created_at)
        )
        return list(self.session.scalars(stmt).all())

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

    def calculate_coverage(self, *, aoi: AOI, layer_id: UUID) -> tuple[float, float]:
        """Return area covered by AIO in square-meter and percentage."""
        stmt_union_features = func.ST_Union(VectorFeature.geometry)
        stmt = (
            select(
                func.ST_Area(
                    cast(
                        func.ST_Intersection(aoi.geometry, stmt_union_features),
                        Geography,
                    )
                ).label("coverage_area_m2"),
                (
                    func.ST_Area(
                        cast(
                            func.ST_Intersection(aoi.geometry, stmt_union_features),
                            Geography,
                        )
                    )
                    / func.ST_Area(cast(stmt_union_features, Geography))
                    * 100
                ).label("coverage_area_percentage"),
            )
            .select_from(VectorFeature)
            .where(VectorFeature.layer_id == layer_id)
        )

        row = self.session.execute(stmt).first()

        if not row or row.coverage_area_m2 is None:
            return (0.0, 0.0)

        return (round(row.coverage_area_m2, 4), round(row.coverage_area_percentage, 4))

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
