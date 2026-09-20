"""
Integration tests for Document Upload and Management REST API.
"""

import io
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_current_active_user, get_db
from app.core.config import get_settings
from app.db.base import Base
from app.main import app
from app.models.user import User

from tests.conftest import TestingSessionLocal

# Test user fixtures
test_user = User(
    id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
    clerk_id="user_test_doc_author",
    email="author@research.org",
    is_active=True,
)


def override_get_current_active_user():
    return test_user


@pytest.fixture(autouse=True)
def setup_test_user():
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    # Seed test user
    db = TestingSessionLocal()
    db.merge(test_user)
    db.commit()
    db.close()
    yield
    app.dependency_overrides.pop(get_current_active_user, None)


@pytest.fixture
def client():
    return TestClient(app)


def test_upload_document_success(client, tmp_path, monkeypatch):
    """Test successful document upload and registration."""
    monkeypatch.setattr(get_settings(), "upload_dir", str(tmp_path))

    file_content = (
        b"# Attention Is All You Need\n\nAbstract: The dominant sequence models..."
    )
    files = {"file": ("attention.md", io.BytesIO(file_content), "text/markdown")}
    data = {"source_mode": "research", "display_title": "Attention Paper"}

    response = client.post("/api/v1/documents/upload", files=files, data=data)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["filename"] == "attention.md"
    assert res_data["display_title"] == "Attention Paper"
    assert res_data["source_mode"] == "research"
    assert res_data["status"] == "pending"
    doc_id = res_data["id"]

    # Retrieve via GET /documents/{id}
    get_res = client.get(f"/api/v1/documents/{doc_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == doc_id


def test_upload_document_invalid_mode_or_extension(client, tmp_path, monkeypatch):
    """Test rejection of invalid source_mode and disallowed file extension."""
    monkeypatch.setattr(get_settings(), "upload_dir", str(tmp_path))

    # 1. Invalid source_mode
    files = {"file": ("test.txt", io.BytesIO(b"content"), "text/plain")}
    response = client.post(
        "/api/v1/documents/upload", files=files, data={"source_mode": "gaming"}
    )
    assert response.status_code == 400
    assert "Invalid source_mode" in response.json()["detail"]

    # 2. Disallowed file extension
    bad_files = {
        "file": ("malicious.exe", io.BytesIO(b"content"), "application/octet-stream")
    }
    bad_res = client.post(
        "/api/v1/documents/upload", files=bad_files, data={"source_mode": "research"}
    )
    assert bad_res.status_code == 400
    assert "Unsupported file type" in bad_res.json()["detail"]


def test_list_and_delete_document(client, tmp_path, monkeypatch):
    """Test listing user documents and deleting."""
    monkeypatch.setattr(get_settings(), "upload_dir", str(tmp_path))

    # Upload two documents
    files1 = {"file": ("doc1.txt", io.BytesIO(b"Doc 1 content"), "text/plain")}
    client.post(
        "/api/v1/documents/upload", files=files1, data={"source_mode": "research"}
    )

    files2 = {"file": ("doc2.txt", io.BytesIO(b"Doc 2 content"), "text/plain")}
    upload2 = client.post(
        "/api/v1/documents/upload", files=files2, data={"source_mode": "study"}
    )
    doc2_id = upload2.json()["id"]

    # List documents
    list_res = client.get("/api/v1/documents")
    assert list_res.status_code == 200
    docs = list_res.json()
    assert len(docs) == 2

    # Delete doc2
    del_res = client.delete(f"/api/v1/documents/{doc2_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "deleted"

    # Confirm list now has 1 document
    list_after = client.get("/api/v1/documents")
    assert len(list_after.json()) == 1

    # Attempt to fetch deleted document returns 404
    fetch_del = client.get(f"/api/v1/documents/{doc2_id}")
    assert fetch_del.status_code == 404
