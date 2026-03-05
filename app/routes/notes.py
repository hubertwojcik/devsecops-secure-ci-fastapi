"""Notes API routes."""

import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Header

from app.models import Note, NoteCreate
from app.store import notes_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_model=list[Note])
def list_notes() -> list[Note]:
    """List all notes."""
    return notes_store.list_notes()


@router.post("", response_model=Note, status_code=201)
def create_note(note_data: NoteCreate) -> Note:
    """Create a new note."""
    return notes_store.create_note(note_data)


@router.get("/{note_id}", response_model=Note)
def get_note(note_id: int) -> Note:
    """Get a specific note by ID."""
    note = notes_store.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


# VULNERABILITY 5: Missing authentication on DELETE endpoint
# This is a logic flaw - anyone can delete any note without authentication
# DAST tools or security audits will identify this as a missing access control
@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int) -> None:
    """Delete a note by ID. No authentication required - SECURITY ISSUE!"""
    if not notes_store.delete_note(note_id):
        raise HTTPException(status_code=404, detail="Note not found")


# FIX: Add authentication to DELETE endpoint
# Uncomment the function below and comment out the one above:
#
# @router.delete("/{note_id}", status_code=204)
# def delete_note_secure(
#     note_id: int,
#     x_api_key: Annotated[str | None, Header()] = None
# ) -> None:
#     """Delete a note by ID with API key authentication."""
#     from app.config import get_settings
#     settings = get_settings()
#     
#     # Validate API key
#     if not x_api_key:
#         raise HTTPException(
#             status_code=401,
#             detail="Missing API key",
#             headers={"WWW-Authenticate": "ApiKey"}
#         )
#     
#     # In production, use secure comparison and proper key management
#     expected_key = os.getenv("API_KEY", "secure-api-key-from-env")
#     if x_api_key != expected_key:
#         raise HTTPException(
#             status_code=403,
#             detail="Invalid API key"
#         )
#     
#     if not notes_store.delete_note(note_id):
#         raise HTTPException(status_code=404, detail="Note not found")
