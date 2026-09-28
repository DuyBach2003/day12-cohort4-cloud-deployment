"""
Tests chạy trong bước "test" của cloudbuild.yaml (pytest tests/ -v).
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready_after_startup():
    with TestClient(app) as c:
        response = c.get("/ready")
        assert response.status_code == 200
        assert response.json()["ready"] is True


def test_ask_requires_question():
    response = client.post("/ask", json={})
    assert response.status_code == 422


def test_ask_returns_answer():
    response = client.post("/ask", json={"question": "Hello"})
    assert response.status_code == 200
    body = response.json()
    assert body["question"] == "Hello"
    assert "answer" in body
