from src.api.app import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_results_today():
    response = client.get("/api/today")
    print(response.status_code)