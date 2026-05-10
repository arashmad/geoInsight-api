from uuid import UUID

from tests.data.data_aoi import MISSING_PROJECT_ID


def test_create_project(client):
    response = client.post(
        "/v1/projects",
        json={
            "name": "Forest Monitoring",
            "description": "Test project",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert UUID(data["id"])
    assert data["name"] == "Forest Monitoring"
    assert data["description"] == "Test project"
    assert "created_at" in data
    assert "updated_at" in data


def test_list_projects(client):
    client.post("/v1/projects", json={"name": "Project A"})
    client.post("/v1/projects", json={"name": "Project B"})

    response = client.get("/v1/projects")

    assert response.status_code == 200

    data = response.json()
    names = {project["name"] for project in data}

    assert "Project A" in names
    assert "Project B" in names


def test_get_project(client):
    create_response = client.post(
        "/v1/projects",
        json={"name": "Project Detail"},
    )
    project_id = create_response.json()["id"]

    response = client.get(f"/v1/projects/{project_id}")

    assert response.status_code == 200
    assert response.json()["id"] == project_id
    assert response.json()["name"] == "Project Detail"


def test_get_missing_project_returns_404(client):
    response = client.get(f"/v1/projects/{MISSING_PROJECT_ID}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_update_project(client):
    create_response = client.post(
        "/v1/projects",
        json={
            "name": "Old Name",
            "description": "Old description",
        },
    )
    project_id = create_response.json()["id"]

    response = client.patch(
        f"/v1/projects/{project_id}",
        json={
            "name": "New Name",
            "description": "New description",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "New Name"
    assert data["description"] == "New description"


def test_update_missing_project_returns_404(client):
    response = client.patch(
        f"/v1/projects/{MISSING_PROJECT_ID}",
        json={"name": "New Name"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_delete_project(client):
    create_response = client.post(
        "/v1/projects",
        json={"name": "Project To Delete"},
    )
    project_id = create_response.json()["id"]

    delete_response = client.delete(f"/v1/projects/{project_id}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/v1/projects/{project_id}")
    assert get_response.status_code == 404


def test_delete_missing_project_returns_404(client):
    response = client.delete(f"/v1/projects/{MISSING_PROJECT_ID}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"
