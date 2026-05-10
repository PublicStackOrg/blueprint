from fastapi.testclient import TestClient

from {{ cookiecutter.python_package }}.main import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "service": "{{ cookiecutter.service_name }}"}
