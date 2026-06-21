from geoinsight_api.db.models.vector_analysis_result import VectorAnalysisResult
from geoinsight_api.db.models.vector_layer import VectorLayer
from geoinsight_api.seeds.land_use import seed_land_use_data
from tests.data.data_aoi import (
    MISSING_AOI_ID,
    MISSING_RESULTS_ID,
    MISSING_VECTOR_LAYER_ID,
)


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
                    [44.4978746, 40.1040156],
                    [44.5012888, 40.1021535],
                    [44.503142, 40.0990132],
                    [44.5083053, 40.0992344],
                    [44.5091366, 40.1018914],
                    [44.5143689, 40.1004173],
                    [44.5124816, 40.104061],
                    [44.5133323, 40.1070111],
                    [44.51, 40.11],
                    [44.5051666, 40.1113229],
                    [44.5010205, 40.1079586],
                    [44.4979615, 40.1077266],
                    [44.4978746, 40.1040156],
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
    assert "grassland" in class_names

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
        f"/v1/aois/{MISSING_AOI_ID}/land-use-composition",
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


def test_get_results_by_id_succeed_200_OK(client, db_session):
    layer = seed_land_use_data(db_session)
    db_session.commit()

    project_id = create_project(client)
    aoi = create_aoi(client, project_id)

    response = client.post(
        f"/v1/aois/{aoi['id']}/land-use-composition",
        json={"layer_id": str(layer.id)},
    )

    data = response.json()

    response = client.get(f"/v1/vector-analysis-results/{data['id']}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"]
    assert data["aoi_id"] == aoi["id"]
    assert data["layer_id"] == str(layer.id)
    assert data["analysis_type"] == "land_use_composition"
    assert data["metrics"]["total_aoi_area_m2"] > 0


def test_get_results_by_aoi_succeed_200_OK(client, db_session):
    layer = seed_land_use_data(db_session)
    db_session.commit()

    project_id = create_project(client)
    aoi = create_aoi(client, project_id)

    response = client.post(
        f"/v1/aois/{aoi['id']}/land-use-composition",
        json={"layer_id": str(layer.id)},
    )

    response = client.post(
        f"/v1/aois/{aoi['id']}/land-use-composition",
        json={"layer_id": str(layer.id)},
    )

    response = client.get(f"/v1/aois/{aoi['id']}/vector-analysis-results")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert data[0]["id"]
    assert data[1]["id"]
    assert data[0]["aoi_id"] == aoi["id"]
    assert data[1]["aoi_id"] == aoi["id"]
    assert data[0]["layer_id"] == str(layer.id)
    assert data[1]["layer_id"] == str(layer.id)
    assert data[0]["analysis_type"] == "land_use_composition"
    assert data[1]["analysis_type"] == "land_use_composition"
    assert data[0]["metrics"]["total_aoi_area_m2"] > 0
    assert data[1]["metrics"]["total_aoi_area_m2"] > 0


def test_get_results_by_aoi_succeed_empty_list_200_OK(client, db_session):
    seed_land_use_data(db_session)
    db_session.commit()

    project_id = create_project(client)
    aoi = create_aoi(client, project_id)

    response = client.get(f"/v1/aois/{aoi['id']}/vector-analysis-results")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 0


def test_get_results_by_id_fail_404_NOT_FOUND(client):
    response = client.get(f"/v1/vector-analysis-results/{MISSING_RESULTS_ID}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Vector analysis results not found"


def test_get_results_by_aoi_fail_404_NOT_FOUND(client):
    response = client.get(f"/v1/aois/{MISSING_AOI_ID}/vector-analysis-results")

    assert response.status_code == 404
    assert response.json()["detail"] == "AOI not found"
