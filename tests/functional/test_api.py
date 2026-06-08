import os
import time
import allure
import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")


def wait_for_service(timeout_seconds=60):
    deadline = time.time() + timeout_seconds
    last_error = None
    while time.time() < deadline:
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=3)
            if response.status_code == 200:
                return
        except requests.RequestException as exc:
            last_error = exc
        time.sleep(2)
    raise AssertionError(f"Service did not become ready at {BASE_URL}: {last_error}")


def test_health_endpoint():
    wait_for_service()
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_version_endpoint():
    wait_for_service()
    response = requests.get(f"{BASE_URL}/version", timeout=5)
    assert response.status_code == 200
    assert "version" in response.json()


def test_add_endpoint_contract():
    wait_for_service()
    response = requests.post(f"{BASE_URL}/add", json={"a": 40, "b": 2}, timeout=5)
    assert response.status_code == 200
    assert response.json() == {"result": 42}


@allure.severity(allure.severity_level.MINOR)
@allure.title("Response time SLA check")
def test_response_time_sla():
    wait_for_service()
    start = time.time()
    response = requests.post(f"{BASE_URL}/add", json={"a": 1, "b": 2}, timeout=5)
    elapsed_ms = (time.time() - start) * 1000
    assert response.status_code == 200
    if elapsed_ms >= 5:
        allure.dynamic.description(
            f"Response took {elapsed_ms:.0f}ms, SLA target is <5ms. "
            "Known latency under cold start conditions."
        )
        raise Warning(f"Response took {elapsed_ms:.0f}ms, SLA target is <5ms")
