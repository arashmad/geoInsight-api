from geoalchemy2.shape import from_shape
from shapely.geometry import MultiPolygon, Polygon
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from geoinsight_api.db.models.vector_feature import VectorFeature
from geoinsight_api.db.models.vector_layer import VectorLayer

LAND_USE_LAYER_NAME = "Demo Land Use"
LAND_USE_LAYER_TYPE = "land_use"
LAND_USE_SOURCE = "seed"


def _multipolygon_from_bounds(
    min_x: float,
    min_y: float,
    max_x: float,
    max_y: float,
) -> MultiPolygon:
    polygon = Polygon(
        [
            (min_x, min_y),
            (max_x, min_y),
            (max_x, max_y),
            (min_x, max_y),
            (min_x, min_y),
        ]
    )

    return MultiPolygon([polygon])


LAND_USE_FEATURES = [
    {
        "class": "forest",
        "geometry": _multipolygon_from_bounds(44.500, 40.100, 44.505, 40.110),
    },
    {
        "class": "agriculture",
        "geometry": _multipolygon_from_bounds(44.505, 40.100, 44.510, 40.105),
    },
    {
        "class": "urban",
        "geometry": _multipolygon_from_bounds(44.505, 40.105, 44.510, 40.110),
    },
    {
        "class": "water",
        "geometry": _multipolygon_from_bounds(44.502, 40.102, 44.508, 40.108),
    },
    {
        "class": "grassland",
        "geometry": _multipolygon_from_bounds(44.510, 40.100, 44.515, 40.110),
    },
]


def seed_land_use_data(session: Session) -> VectorLayer:
    layer = session.scalar(
        select(VectorLayer).where(
            VectorLayer.name == LAND_USE_LAYER_NAME,
            VectorLayer.layer_type == LAND_USE_LAYER_TYPE,
            VectorLayer.source == LAND_USE_SOURCE,
        )
    )

    if layer is None:
        layer = VectorLayer(
            name=LAND_USE_LAYER_NAME,
            description="Controlled demo land-use layer for spatial analysis tests",
            layer_type=LAND_USE_LAYER_TYPE,
            source=LAND_USE_SOURCE,
            srid=4326,
            properties_schema={"class": "string"},
        )
        session.add(layer)
        session.flush()
    else:
        layer.description = "Controlled demo land-use layer for spatial analysis tests"
        layer.srid = 4326
        layer.properties_schema = {"class": "string"}
        session.flush()

    session.execute(delete(VectorFeature).where(VectorFeature.layer_id == layer.id))

    for feature_data in LAND_USE_FEATURES:
        feature = VectorFeature(
            layer_id=layer.id,
            geometry=from_shape(feature_data["geometry"], srid=4326),
            properties={"class": feature_data["class"]},
        )
        session.add(feature)

    session.commit()
    session.refresh(layer)

    return layer
