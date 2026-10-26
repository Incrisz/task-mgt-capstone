import pytest
from app.main import create_app, db

@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}"})
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.session.remove()
        db.drop_all()

def test_health_and_ready(client):
    assert client.get("/health").json == {"status": "ok"}
    assert client.get("/ready").status_code == 200

def test_create_list_update_delete(client):
    response = client.post("/api/tasks", json={"title": "Ship pipeline", "description": "CI first"})
    assert response.status_code == 201
    task_id = response.json["id"]
    assert response.json["status"] == "todo"
    assert len(client.get("/api/tasks").json["tasks"]) == 1
    assert client.get(f"/api/tasks/{task_id}").status_code == 200
    assert client.patch(f"/api/tasks/{task_id}", json={"status": "done"}).json["status"] == "done"
    assert len(client.get("/api/tasks?status=done").json["tasks"]) == 1
    assert client.delete(f"/api/tasks/{task_id}").status_code == 204
    assert client.get(f"/api/tasks/{task_id}").status_code == 404

def test_invalid_requests(client):
    assert client.post("/api/tasks", json={"title": ""}).status_code == 400
    assert client.post("/api/tasks", json={"title": "T", "status": "unknown"}).status_code == 400
    assert client.post("/api/tasks", data="not json").status_code == 400
    assert client.get("/api/tasks?status=bad").status_code == 400
