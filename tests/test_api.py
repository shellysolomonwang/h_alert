from fastapi.testclient import TestClient

from app.main import app


def test_home_page(monkeypatch):
    monkeypatch.setattr("app.main.get_available_bags", lambda: {"birkin 25": True, "lindy mini": False})
    client = TestClient(app)

    resp = client.get("/")
    assert resp.status_code == 200
    assert "Create Subscription" in resp.text
    assert "birkin 25" in resp.text
