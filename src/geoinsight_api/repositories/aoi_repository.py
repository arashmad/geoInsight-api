from typing import Any
from uuid import UUID

from geoalchemy2.shape import from_shape
from shapely.geometry import MultiPolygon, Point
from sqlalchemy import select
from sqlalchemy.orm import Session

from geoinsight_api.db.models.aoi import AOI


class AOIRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        project_id: UUID,
        name: str,
        geometry: MultiPolygon,
        area_m2: float,
        centroid: Point,
        bbox: list[float],
    ) -> AOI:
        aoi = AOI(
            project_id=project_id,
            name=name,
            geometry=from_shape(geometry, srid=4326),
            area_m2=area_m2,
            centroid=from_shape(centroid, srid=4326),
            bbox=bbox,
        )

        self.session.add(aoi)
        self.session.flush()

        return aoi

    def list_by_project_id(self, project_id: UUID) -> list[AOI]:
        stmt = (
            select(AOI)
            .where(AOI.project_id == project_id)
            .order_by(AOI.created_at.desc())
        )
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, aoi_id: UUID) -> AOI | None:
        return self.session.get(AOI, aoi_id)

    def update(self, aoi: AOI, data: dict[str, Any]) -> AOI:
        for field, value in data.items():
            setattr(aoi, field, value)

        self.session.flush()
        return aoi

    # TODO: Maybe marry this to `update` is cleaner
    def update_geometry(
        self,
        aoi: AOI,
        *,
        geometry: MultiPolygon,
        area_m2: float,
        centroid: Point,
        bbox: list[float],
    ) -> AOI:
        aoi.geometry = from_shape(geometry, srid=4326)
        aoi.area_m2 = area_m2
        aoi.centroid = from_shape(centroid, srid=4326)
        aoi.bbox = bbox

        self.session.flush()
        return aoi

    def delete(self, aoi: AOI) -> None:
        self.session.delete(aoi)
        self.session.flush()
