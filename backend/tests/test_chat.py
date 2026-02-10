"""Test suite for the chat API endpoints."""
import pytest
from fastapi.testclient import TestClient
from main import app
import uuid


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


def test_chat_endpoint_exists(client):
    """Test that the chat endpoint exists."""
    # Test without auth should return 401
    response = client.post("/api/v1/chat", json={"message": "hello"})
    assert response.status_code == 401  # Unauthorized without token


def test_chat_conversations_endpoint_exists(client):
    """Test that the chat conversations endpoint exists."""
    # Test without auth should return 401
    response = client.get("/api/v1/conversations")
    assert response.status_code == 401  # Unauthorized without token


def test_chat_conversation_detail_endpoint_exists(client):
    """Test that the chat conversation detail endpoint exists."""
    # Test without auth should return 401
    fake_uuid = str(uuid.uuid4())
    response = client.get(f"/api/v1/conversations/{fake_uuid}")
    assert response.status_code == 401  # Unauthorized without token


def test_chat_conversation_delete_endpoint_exists(client):
    """Test that the chat conversation delete endpoint exists."""
    # Test without auth should return 401
    fake_uuid = str(uuid.uuid4())
    response = client.delete(f"/api/v1/conversations/{fake_uuid}")
    assert response.status_code == 401  # Unauthorized without token


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"