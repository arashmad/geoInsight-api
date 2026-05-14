from geoalchemy2.shape import from_shape
from shapely.geometry import MultiPolygon, Polygon
from sqlalchemy import func, select

from geoinsight_api.db.models.aoi import AOI
from geoinsight_api.db.models.project import Project
from geoinsight_api.db.models.vector_feature import VectorFeature
from geoinsight_api.db.models.vector_layer import VectorLayer
from geoinsight_api.seeds.land_use import (
    LAND_USE_LAYER_NAME,
    LAND_USE_LAYER_TYPE,
    LAND_USE_SOURCE,
    seed_land_use_data,
)


def test_seed_land_use_creates_layer_and_features(db_session):
    layer = seed_land_use_data(db_session)

    saved_layer = db_session.get(VectorLayer, layer.id)

    assert saved_layer is not None
    assert saved_layer.name == LAND_USE_LAYER_NAME
    assert saved_layer.layer_type == LAND_USE_LAYER_TYPE
    assert saved_layer.source == LAND_USE_SOURCE
    assert saved_layer.srid == 4326
    assert saved_layer.properties_schema == {"class": "string"}

    features = list(
        db_session.scalars(
            select(VectorFeature).where(VectorFeature.layer_id == saved_layer.id)
        ).all()
    )

    assert len(features) == 5

    classes = {feature.properties["class"] for feature in features}

    assert classes == {
        "forest",
        "agriculture",
        "urban",
        "water",
        "grassland",
    }


def test_seed_land_use_is_idempotent(db_session):
    first_layer = seed_land_use_data(db_session)
    second_layer = seed_land_use_data(db_session)

    assert first_layer.id == second_layer.id

    layers = list(
        db_session.scalars(
            select(VectorLayer).where(
                VectorLayer.name == LAND_USE_LAYER_NAME,
                VectorLayer.layer_type == LAND_USE_LAYER_TYPE,
                VectorLayer.source == LAND_USE_SOURCE,
            )
        ).all()
    )

    assert len(layers) == 1

    features = list(
        db_session.scalars(
            select(VectorFeature).where(VectorFeature.layer_id == second_layer.id)
        ).all()
    )

    assert len(features) == 5


def test_seeded_land_use_features_spatially_overlap_test_aoi(db_session):
    layer = seed_land_use_data(db_session)

    project = Project(name="Seed overlap test project")
    db_session.add(project)
    db_session.flush()

    aoi_polygon = Polygon(
        [
            (44.50, 40.10),
            (44.51, 40.10),
            (44.51, 40.11),
            (44.50, 40.11),
            (44.50, 40.10),
        ]
    )

    aoi = AOI(
        project_id=project.id,
        name="Seed overlap AOI",
        geometry=from_shape(MultiPolygon([aoi_polygon]), srid=4326),
        area_m2=1.0,
        centroid=from_shape(aoi_polygon.centroid, srid=4326),
        bbox=[44.50, 40.10, 44.51, 40.11],
    )
    db_session.add(aoi)
    db_session.flush()

    overlap_count = db_session.scalar(
        select(func.count(VectorFeature.id))
        .where(VectorFeature.layer_id == layer.id)
        .where(func.ST_Intersects(VectorFeature.geometry, aoi.geometry))
    )

    assert overlap_count is not None
    assert overlap_count > 0
