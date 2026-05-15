
from geoinsight_api.db.models.vector_analysis_result import VectorAnalysisResult
from geoinsight_api.db.models.vector_layer import VectorLayer
from geoinsight_api.seeds.land_use import seed_land_use_data
from tests.data.data_aoi import MISSING_PROJECT_ID, MISSING_VECTOR_LAYER_ID


def create_project(client) -> str:
    response = client.post(
        "/v1/projects",
        json={"name": "Land-use analysis project"},
    )

    assert response.status_code == 201
    return response.json()["id"]


def create_aoi(client, project_id: str, geometry: dict | None = None) -> dict:
    if geometry is None:
        geometry = {
            "type": "Polygon",
            "coordinates": [
                [
                    [44.50, 40.10],
                    [44.51, 40.10],
                    [44.51, 40.11],
                    [44.50, 40.11],
                    [44.50, 40.10],
                ]
            ],
        }

    response = client.post(
        f"/v1/projects/{project_id}/aois",
        json={
            "name": "Land-use AOI",
            "geometry": geometry,
        },
    )

    assert response.status_code == 201
    return response.json()


def test_run_land_use_composition_persists_and_returns_result(client, db_session):
    layer = seed_land_use_data(db_session)
    db_session.commit()

    project_id = create_project(client)
    aoi = create_aoi(client, project_id)

    response = client.post(
        f"/v1/aois/{aoi['id']}/land-use-composition",
        json={"layer_id": str(layer.id)},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"]
    assert data["aoi_id"] == aoi["id"]
    assert data["layer_id"] == str(layer.id)
    assert data["analysis_type"] == "land_use_composition"
    assert data["metrics"]["total_aoi_area_m2"] > 0

    classes = data["metrics"]["classes"]
    class_names = {item["class"] for item in classes}

    assert "forest" in class_names
    assert "agriculture" in class_names
    assert "urban" in class_names
    assert "water" in class_names

    for item in classes:
        assert item["area_m2"] > 0
        assert item["percentage"] > 0

    saved_result = db_session.get(VectorAnalysisResult, data["id"])

    assert saved_result is not None
    assert saved_result.analysis_type == "land_use_composition"


def test_run_land_use_composition_for_missing_aoi_returns_404(client, db_session):
    layer = seed_land_use_data(db_session)
    db_session.commit()

    response = client.post(
        f"/v1/aois/{MISSING_PROJECT_ID}/land-use-composition",
        json={"layer_id": str(layer.id)},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "AOI not found"


def test_run_land_use_composition_for_missing_layer_returns_404(client):
    project_id = create_project(client)
    aoi = create_aoi(client, project_id)

    response = client.post(
        f"/v1/aois/{aoi['id']}/land-use-composition",
        json={"layer_id": MISSING_VECTOR_LAYER_ID},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Vector layer not found"


def test_run_land_use_composition_with_invalid_layer_type_returns_422(
    client,
    db_session,
):
    layer = VectorLayer(
        name="Roads",
        layer_type="road",
        source="test",
        srid=4326,
    )
    db_session.add(layer)
    db_session.commit()

    project_id = create_project(client)
    aoi = create_aoi(client, project_id)

    response = client.post(
        f"/v1/aois/{aoi['id']}/land-use-composition",
        json={"layer_id": str(layer.id)},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Vector layer must have layer_type='land_use'"


def test_run_land_use_composition_with_no_overlap_returns_empty_classes(
    client,
    db_session,
):
    layer = seed_land_use_data(db_session)
    db_session.commit()

    project_id = create_project(client)

    far_away_geometry = {
        "type": "Polygon",
        "coordinates": [
            [
                [45.00, 41.00],
                [45.01, 41.00],
                [45.01, 41.01],
                [45.00, 41.01],
                [45.00, 41.00],
            ]
        ],
    }

    aoi = create_aoi(client, project_id, geometry=far_away_geometry)

    response = client.post(
        f"/v1/aois/{aoi['id']}/land-use-composition",
        json={"layer_id": str(layer.id)},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["metrics"]["classes"] == []
    assert data["metrics"]["total_aoi_area_m2"] > 0
