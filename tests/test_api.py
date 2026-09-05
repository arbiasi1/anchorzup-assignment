import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Rule


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base.metadata.create_all(engine)


def override_get_db():
    with TestingSession() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_rules():
    with TestingSession() as session:
        session.execute(delete(Rule))
        session.commit()


def highlight_rule(keyword: str = "urgent") -> dict:
    return {
        "keyword": keyword,
        "match_type": "exact",
        "action_type": "highlight",
        "color": "#ff0000",
        "priority": 10,
        "enabled": True,
        "case_sensitive": False,
    }


def test_health_checks_database_connection():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_rule_crud_lifecycle():
    created = client.post("/api/rules", json=highlight_rule())
    assert created.status_code == 201
    rule_id = created.json()["id"]

    listed = client.get("/api/rules")
    assert listed.status_code == 200
    assert [rule["keyword"] for rule in listed.json()] == ["urgent"]

    updated = client.put(f"/api/rules/{rule_id}", json={"enabled": False})
    assert updated.status_code == 200
    assert updated.json()["enabled"] is False

    deleted = client.delete(f"/api/rules/{rule_id}")
    assert deleted.status_code == 204
    assert client.get("/api/rules").json() == []


def test_process_uses_all_enabled_rules():
    client.post("/api/rules", json=highlight_rule())
    client.post("/api/rules", json={
        "keyword": "deadline",
        "match_type": "contains",
        "action_type": "tooltip",
        "label": "IMPORTANT",
        "priority": 5,
        "enabled": True,
        "case_sensitive": False,
    })

    response = client.post("/api/process", json={"text": "The deadline is urgent."})

    assert response.status_code == 200
    data = response.json()
    assert data["match_count"] == 2
    assert data["matched_rule_count"] == 2
    assert {match["action_type"] for segment in data["segments"] for match in segment["matches"]} == {
        "highlight", "tooltip"
    }


def test_invalid_rule_is_rejected():
    payload = highlight_rule()
    payload["color"] = "red"

    response = client.post("/api/rules", json=payload)

    assert response.status_code == 422


def test_missing_rule_returns_not_found():
    response = client.put("/api/rules/999", json={"enabled": False})

    assert response.status_code == 404
    assert response.json()["detail"] == "Rule not found"
