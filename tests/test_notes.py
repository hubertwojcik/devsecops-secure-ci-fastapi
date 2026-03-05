"""Tests for notes API endpoints."""

from fastapi.testclient import TestClient


def test_list_notes_empty(client: TestClient):
    """Test listing notes when store is empty."""
    response = client.get("/notes")
    assert response.status_code == 200
    assert response.json() == []


def test_create_note_success(client: TestClient):
    """Test creating a note successfully."""
    note_data = {
        "title": "Test Note",
        "content": "This is a test note content"
    }
    response = client.post("/notes", json=note_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == note_data["title"]
    assert data["content"] == note_data["content"]
    assert "created_at" in data


def test_create_note_with_max_length_title(client: TestClient):
    """Test creating a note with maximum length title."""
    note_data = {
        "title": "A" * 100,  # Max length
        "content": "Content"
    }
    response = client.post("/notes", json=note_data)
    assert response.status_code == 201


def test_create_note_with_max_length_content(client: TestClient):
    """Test creating a note with maximum length content."""
    note_data = {
        "title": "Title",
        "content": "B" * 5000  # Max length
    }
    response = client.post("/notes", json=note_data)
    assert response.status_code == 201


def test_create_note_empty_title_fails(client: TestClient):
    """Test creating a note with empty title fails validation."""
    note_data = {
        "title": "",
        "content": "Content"
    }
    response = client.post("/notes", json=note_data)
    assert response.status_code == 422


def test_create_note_title_too_long_fails(client: TestClient):
    """Test creating a note with title exceeding max length fails."""
    note_data = {
        "title": "A" * 101,  # Over max length
        "content": "Content"
    }
    response = client.post("/notes", json=note_data)
    assert response.status_code == 422


def test_create_note_content_too_long_fails(client: TestClient):
    """Test creating a note with content exceeding max length fails."""
    note_data = {
        "title": "Title",
        "content": "B" * 5001  # Over max length
    }
    response = client.post("/notes", json=note_data)
    assert response.status_code == 422


def test_create_note_missing_title_fails(client: TestClient):
    """Test creating a note without title fails."""
    note_data = {
        "content": "Content"
    }
    response = client.post("/notes", json=note_data)
    assert response.status_code == 422


def test_create_note_missing_content_fails(client: TestClient):
    """Test creating a note without content fails."""
    note_data = {
        "title": "Title"
    }
    response = client.post("/notes", json=note_data)
    assert response.status_code == 422


def test_list_notes_with_data(client: TestClient):
    """Test listing notes after creating some."""
    # Create multiple notes
    notes = [
        {"title": "Note 1", "content": "Content 1"},
        {"title": "Note 2", "content": "Content 2"},
        {"title": "Note 3", "content": "Content 3"}
    ]
    
    for note in notes:
        client.post("/notes", json=note)
    
    response = client.get("/notes")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 3
    assert all("id" in note for note in data)
    assert all("created_at" in note for note in data)


def test_get_note_by_id_success(client: TestClient):
    """Test getting a specific note by ID."""
    # Create a note
    note_data = {"title": "Test", "content": "Content"}
    create_response = client.post("/notes", json=note_data)
    note_id = create_response.json()["id"]
    
    # Get the note
    response = client.get(f"/notes/{note_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == note_data["title"]
    assert data["content"] == note_data["content"]


def test_get_note_not_found(client: TestClient):
    """Test getting a non-existent note returns 404."""
    response = client.get("/notes/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_note_success(client: TestClient):
    """Test deleting a note successfully."""
    # Create a note
    note_data = {"title": "To Delete", "content": "Will be deleted"}
    create_response = client.post("/notes", json=note_data)
    note_id = create_response.json()["id"]
    
    # Delete the note
    response = client.delete(f"/notes/{note_id}")
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(f"/notes/{note_id}")
    assert get_response.status_code == 404


def test_delete_note_not_found(client: TestClient):
    """Test deleting a non-existent note returns 404."""
    response = client.delete("/notes/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_note_no_authentication_required(client: TestClient):
    """
    Test that DELETE endpoint does not require authentication.
    This is a SECURITY VULNERABILITY - anyone can delete notes!
    """
    # Create a note
    note_data = {"title": "Unprotected", "content": "Can be deleted by anyone"}
    create_response = client.post("/notes", json=note_data)
    note_id = create_response.json()["id"]
    
    # Delete without any authentication headers
    response = client.delete(f"/notes/{note_id}")
    assert response.status_code == 204  # Success without auth - this is the vulnerability!


def test_create_multiple_notes_incremental_ids(client: TestClient):
    """Test that note IDs increment correctly."""
    note1 = client.post("/notes", json={"title": "First", "content": "1"}).json()
    note2 = client.post("/notes", json={"title": "Second", "content": "2"}).json()
    note3 = client.post("/notes", json={"title": "Third", "content": "3"}).json()
    
    assert note1["id"] == 1
    assert note2["id"] == 2
    assert note3["id"] == 3


def test_note_timestamps_are_set(client: TestClient):
    """Test that created_at timestamps are set correctly."""
    import datetime
    
    before = datetime.datetime.utcnow()
    response = client.post("/notes", json={"title": "Time Test", "content": "Content"})
    after = datetime.datetime.utcnow()
    
    data = response.json()
    created_at = datetime.datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
    
    assert before <= created_at <= after


def test_notes_persist_across_requests(client: TestClient):
    """Test that notes persist in memory across multiple requests."""
    # Create a note
    create_response = client.post("/notes", json={"title": "Persist", "content": "Test"})
    note_id = create_response.json()["id"]
    
    # Make multiple GET requests
    for _ in range(3):
        response = client.get(f"/notes/{note_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Persist"
