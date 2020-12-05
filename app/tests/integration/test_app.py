from uuid import UUID
from fastapi.testclient import TestClient

from app.app import app

client = TestClient(app)


def test_create_session():
    response = client.post("/session")
    body = response.json()

    assert response.status_code == 201
    assert 'session_id' in body
    UUID(body['session_id'])

def test_joining_non_existing_session():
    response = client.post('/session/no-existo/user')

    assert response.status_code == 404
