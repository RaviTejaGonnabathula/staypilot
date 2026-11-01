from fastapi.testclient import TestClient
from staypilot_gateway.main import create_app


def test_gateway_health() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "staypilot-gateway",
    }
