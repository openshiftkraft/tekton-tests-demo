import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.parametrize("a,b,expected", [(1, 2, 3), (-5, 2, -3), (1.5, 2.25, 3.75)])
def test_add_returns_sum(a, b, expected):
    response = client.post("/add", json={"a": a, "b": b})
    assert response.status_code == 200
    assert response.json()["result"] == expected


def test_add_rejects_huge_result():
    response = client.post("/add", json={"a": 1_000_000, "b": 1})
    assert response.status_code == 400
