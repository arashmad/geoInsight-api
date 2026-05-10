from typing import Any

from pyproj import Geod
from shapely.geometry import MultiPolygon, Polygon, mapping, shape
from shapely.geometry.base import BaseGeometry
from shapely.validation import explain_validity
from shapely.ops import orient


class InvalidGeometryError(Exception):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


class UnsupportedGeometryTypeError(Exception):
    pass


WGS84_GEOD = Geod(ellps="WGS84")


def parse_geojson_geometry(geometry: dict[str, Any]) -> BaseGeometry:
    try:
        parsed = shape(geometry)
    except Exception as exc:
        raise InvalidGeometryError("Invalid GeoJSON geometry") from exc

    if not isinstance(parsed, Polygon | MultiPolygon):
        raise UnsupportedGeometryTypeError

    if parsed.is_empty:
        raise InvalidGeometryError("Geometry is empty")

    if not parsed.is_valid:
        raise InvalidGeometryError(explain_validity(parsed))

    return parsed


def normalize_to_multipolygon(geometry: BaseGeometry) -> MultiPolygon:
    if isinstance(geometry, Polygon):
        return MultiPolygon([geometry])

    if isinstance(geometry, MultiPolygon):
        return geometry

    raise UnsupportedGeometryTypeError


def calculate_area_m2(geometry: BaseGeometry) -> float:
    if isinstance(geometry, Polygon):
        area, _ = WGS84_GEOD.geometry_area_perimeter(orient(geometry, sign=1.0))
        return abs(area)

    if isinstance(geometry, MultiPolygon):
        total = 0.0

        for polygon in geometry.geoms:
            area, _ = WGS84_GEOD.geometry_area_perimeter(orient(polygon, sign=1.0))
            total += abs(area)

        return total

    raise UnsupportedGeometryTypeError


def calculate_centroid_geojson(geometry: BaseGeometry) -> dict[str, Any]:
    return mapping(geometry.centroid)


def calculate_bbox(geometry: BaseGeometry) -> list[float]:
    min_x, min_y, max_x, max_y = geometry.bounds
    return [min_x, min_y, max_x, max_y]


def to_geojson(geometry: BaseGeometry) -> dict[str, Any]:
    return mapping(geometry)