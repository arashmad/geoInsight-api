from typing import Any
from uuid import UUID

from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from geoinsight_api.db.models.aoi import AOI
from geoinsight_api.db.models.project import Project
from geoinsight_api.repositories.aoi_repository import AOIRepository
from geoinsight_api.services.geometry_service import (
    calculate_area_m2,
    calculate_bbox,
    normalize_to_multipolygon,
    parse_geojson_geometry,
    to_geojson,
)


class ProjectNotFoundError(Exception):
    pass


class AOIService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = AOIRepository(session)

    def create_aoi(
        self,
        *,
        project_id: UUID,
        name: str,
        geometry: dict[str, Any],
    ) -> AOI:
        project = self.session.get(Project, project_id)

        if project is None:
            raise ProjectNotFoundError

        parsed_geometry = parse_geojson_geometry(geometry)
        normalized_geometry = normalize_to_multipolygon(parsed_geometry)

        area_m2 = calculate_area_m2(normalized_geometry)
        centroid = normalized_geometry.centroid
        bbox = calculate_bbox(normalized_geometry)

        aoi = self.repository.create(
            project_id=project_id,
            name=name,
            geometry=normalized_geometry,
            area_m2=area_m2,
            centroid=centroid,
            bbox=bbox,
        )

        self.session.commit()
        self.session.refresh(aoi)

        return aoi

    def to_response(self, aoi: AOI) -> dict[str, Any]:
        geometry = to_shape(aoi.geometry)
        centroid = to_shape(aoi.centroid)

        return {
            "id": aoi.id,
            "project_id": aoi.project_id,
            "name": aoi.name,
            "geometry": to_geojson(geometry),
            "area_m2": aoi.area_m2,
            "centroid": to_geojson(centroid),
            "bbox": aoi.bbox,
            "created_at": aoi.created_at,
            "updated_at": aoi.updated_at,
        }