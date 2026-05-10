from decimal import Decimal
from uuid import UUID

from geoalchemy2.shape import from_shape
from shapely.geometry import MultiPolygon, Point
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