from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import MultiPolygon, Polygon

from geoinsight_api.db.models.vector_feature import VectorFeature
from geoinsight_api.db.models.vector_layer import VectorLayer


def test_create_vector_layer_with_feature(db_session):
    layer = VectorLayer(
        name="Demo Land Use",
        description="Controlled test land-use layer",
        layer_type="land_use",
        source="test",
        srid=4326,
        properties_schema={
            "class": "string",
        },
    )

    db_session.add(layer)
    db_session.flush()

    polygon = Polygon(
        [
            (44.50, 40.10),
            (44.51, 40.10),
            (44.51, 40.11),
            (44.50, 40.11),
            (44.50, 40.10),
        ]
    )

    feature = VectorFeature(
        layer_id=layer.id,
        geometry=from_shape(MultiPolygon([polygon]), srid=4326),
        properties={
            "class": "forest",
        },
    )

    db_session.add(feature)
    db_session.commit()

    saved_feature = db_session.get(VectorFeature, feature.id)

    assert saved_feature is not None
    assert saved_feature.layer_id == layer.id
    assert saved_feature.properties["class"] == "forest"

    saved_geometry = to_shape(saved_feature.geometry)

    assert saved_geometry.geom_type == "MultiPolygon"
    assert not saved_geometry.is_empty
