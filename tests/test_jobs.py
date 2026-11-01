from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200

def test_jobs_endpoint():
    response = client.get("/jobs/?limit=5")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body

def test_stats_overview():
    response = client.get("/stats/overview")
    assert response.status_code == 200