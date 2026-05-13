from tests.data.data_aoi import MISSING_VECTOR_LAYER_ID


def create_vector_layer(client, name: str = "Demo Land Use") -> dict:
    response = client.post(
        "/v1/vector-layers",
        json={
            "name": name,
            "description": "Controlled land-use metadata layer",
            "layer_type": "land_use",
            "source": "test",
            "srid": 4326,
            "properties_schema": {
                "class": "string",
            },
        },
    )

    assert response.status_code == 201
    return response.json()


def test_create_vector_layer(client):
    response = client.post(
        "/v1/vector-layers",
        json={
            "name": "Demo Land Use",
            "description": "Controlled land-use metadata layer",
            "layer_type": "land_use",
            "source": "test",
            "srid": 4326,
            "properties_schema": {
                "class": "string",
            },
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"]
    assert data["name"] == "Demo Land Use"
    assert data["description"] == "Controlled land-use metadata layer"
    assert data["layer_type"] == "land_use"
    assert data["source"] == "test"
    assert data["srid"] == 4326
    assert data["properties_schema"] == {"class": "string"}
    assert data["created_at"]
    assert data["updated_at"]


def test_list_vector_layers(client):
    create_vector_layer(client, "Land Use A")
    create_vector_layer(client, "Land Use B")

    response = client.get("/v1/vector-layers")

    assert response.status_code == 200

    data = response.json()
    names = {layer["name"] for layer in data}

    assert "Land Use A" in names
    assert "Land Use B" in names


def test_get_vector_layer(client):
    created_layer = create_vector_layer(client, "Detail Land Use")

    response = client.get(f"/v1/vector-layers/{created_layer['id']}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == created_layer["id"]
    assert data["name"] == "Detail Land Use"
    assert data["layer_type"] == "land_use"


def test_get_missing_vector_layer_returns_404(client):
    response = client.get(f"/v1/vector-layers/{MISSING_VECTOR_LAYER_ID}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Vector layer not found"


def test_delete_vector_layer(client):
    created_layer = create_vector_layer(client, "Delete Land Use")

    delete_response = client.delete(f"/v1/vector-layers/{created_layer['id']}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/v1/vector-layers/{created_layer['id']}")
    assert get_response.status_code == 404


def test_delete_missing_vector_layer_returns_404(client):
    response = client.delete(f"/v1/vector-layers/{MISSING_VECTOR_LAYER_ID}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Vector layer not found"
