from tests.data.data_aoi import (
    INVALID_POLYGON,
    MISSING_AOI_ID,
    MISSING_PROJECT_ID,
    UPDATED_POLYGON,
    VALID_MULTIPOLYGON,
    VALID_POLYGON,
)


def create_project(client) -> str:
    response = client.post(
        "/v1/projects",
        json={"name": "AOI Test Project"},
    )

    assert response.status_code == 201
    return response.json()["id"]


def create_aoi(client, project_id: str, name: str = "Test AOI") -> dict:
    response = client.post(
        f"/v1/projects/{project_id}/aois",
        json={
            "name": name,
            "geometry": VALID_POLYGON,
        },
    )

    assert response.status_code == 201
    return response.json()


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
    assert (
        response.json()["detail"]
        == "Only Polygon and MultiPolygon geometries are supported"
    )


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


def test_list_aois_by_project(client):
    project_id = create_project(client)

    create_aoi(client, project_id, "AOI A")
    create_aoi(client, project_id, "AOI B")

    response = client.get(f"/v1/projects/{project_id}/aois")

    assert response.status_code == 200

    data = response.json()
    names = {aoi["name"] for aoi in data}

    assert "AOI A" in names
    assert "AOI B" in names


def test_list_aois_for_missing_project_returns_404(client):
    response = client.get(f"/v1/projects/{MISSING_PROJECT_ID}/aois")

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_get_aoi(client):
    project_id = create_project(client)
    created_aoi = create_aoi(client, project_id, "Detail AOI")

    response = client.get(f"/v1/aois/{created_aoi['id']}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == created_aoi["id"]
    assert data["name"] == "Detail AOI"
    assert data["project_id"] == project_id


def test_get_missing_aoi_returns_404(client):
    response = client.get(f"/v1/aois/{MISSING_AOI_ID}")

    assert response.status_code == 404
    assert response.json()["detail"] == "AOI not found"


def test_update_aoi_name(client):
    project_id = create_project(client)
    created_aoi = create_aoi(client, project_id, "Old AOI Name")

    response = client.patch(
        f"/v1/aois/{created_aoi['id']}",
        json={"name": "Updated AOI Name"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == created_aoi["id"]
    assert data["name"] == "Updated AOI Name"
    assert data["geometry"] == created_aoi["geometry"]


def test_update_aoi_geometry_recalculates_derived_fields(client):
    project_id = create_project(client)
    created_aoi = create_aoi(client, project_id, "Geometry Update AOI")

    response = client.patch(
        f"/v1/aois/{created_aoi['id']}",
        json={"geometry": UPDATED_POLYGON},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == created_aoi["id"]
    assert data["geometry"]["type"] == "MultiPolygon"
    assert data["area_m2"] != created_aoi["area_m2"]
    assert data["centroid"] != created_aoi["centroid"]
    assert data["bbox"] != created_aoi["bbox"]


def test_update_missing_aoi_returns_404(client):
    response = client.patch(
        f"/v1/aois/{MISSING_AOI_ID}",
        json={"name": "Updated Name"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "AOI not found"


def test_update_aoi_with_invalid_geometry_returns_422(client):
    project_id = create_project(client)
    created_aoi = create_aoi(client, project_id)

    response = client.patch(
        f"/v1/aois/{created_aoi['id']}",
        json={"geometry": INVALID_POLYGON},
    )

    assert response.status_code == 422
    assert "Invalid geometry" in response.json()["detail"]


def test_delete_aoi(client):
    project_id = create_project(client)
    created_aoi = create_aoi(client, project_id, "Delete AOI")

    delete_response = client.delete(f"/v1/aois/{created_aoi['id']}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/v1/aois/{created_aoi['id']}")
    assert get_response.status_code == 404


def test_delete_missing_aoi_returns_404(client):
    response = client.delete(f"/v1/aois/{MISSING_AOI_ID}")

    assert response.status_code == 404
    assert response.json()["detail"] == "AOI not found"
