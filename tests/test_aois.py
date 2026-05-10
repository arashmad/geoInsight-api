from tests.data.data_aoi import (
    VALID_POLYGON,
    VALID_MULTIPOLYGON,
    INVALID_POLYGON,
    MISSING_PROJECT_ID
)

def create_project(client) -> str:
    response = client.post(
        "/v1/projects",
        json={"name": "AOI Test Project"},
    )

    assert response.status_code == 201
    return response.json()["id"]

def test_create_aoi_with_valid_polygon(client):
    project_id = create_project(client)

    response = client.post(
        f"/v1/projects/{project_id}/aois",
        json={
            "name": "Test Polygon AOI",
            "geometry": VALID_POLYGON,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["project_id"] == project_id
    assert data["name"] == "Test Polygon AOI"
    assert data["geometry"]["type"] == "MultiPolygon"
    assert data["area_m2"] > 0
    assert data["centroid"]["type"] == "Point"
    assert len(data["bbox"]) == 4

def test_create_aoi_with_valid_multipolygon(client):
    project_id = create_project(client)

    response = client.post(
        f"/v1/projects/{project_id}/aois",
        json={
            "name": "Test MultiPolygon AOI",
            "geometry": VALID_MULTIPOLYGON,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["geometry"]["type"] == "MultiPolygon"
    assert data["area_m2"] > 0
    assert data["centroid"]["type"] == "Point"
    assert len(data["bbox"]) == 4

def test_create_aoi_with_invalid_geometry_returns_422(client):
    project_id = create_project(client)

    response = client.post(
        f"/v1/projects/{project_id}/aois",
        json={
            "name": "Invalid AOI",
            "geometry": INVALID_POLYGON,
        },
    )

    assert response.status_code == 422
    assert "Invalid geometry" in response.json()["detail"]

def test_create_aoi_with_unsupported_geometry_returns_422(client):
    project_id = create_project(client)

    response = client.post(
        f"/v1/projects/{project_id}/aois",
        json={
            "name": "Invalid AOI",
            "geometry": {
                "type": "Point",
                "coordinates": [44.50, 40.10],
            },
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Only Polygon and MultiPolygon geometries are supported"

def test_create_aoi_for_missing_project_returns_404(client):
    response = client.post(
        f"/v1/projects/{MISSING_PROJECT_ID}/aois",
        json={
            "name": "Orphan AOI",
            "geometry": VALID_POLYGON,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"

# TODO: Add persistence test -> AOI in DB
