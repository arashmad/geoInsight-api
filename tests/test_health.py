from fastapi.testclient import  TestClient

from geoinsight_api.main import app

client = TestClient(app)

def test_endpoint_health():
    """Test [GET] health endpoint -> 200_OK"""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

