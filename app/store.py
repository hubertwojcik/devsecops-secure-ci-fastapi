"""In-memory data store for notes."""

import logging
from datetime import datetime
from typing import Optional

from app.models import Note, NoteCreate

logger = logging.getLogger(__name__)


class NotesStore:
    """In-memory storage for notes."""
    
    def __init__(self) -> None:
        self._notes: dict[int, Note] = {}
        self._next_id: int = 1
    
    def create_note(self, note_data: NoteCreate) -> Note:
        """Create a new note."""
        note = Note(
            id=self._next_id,
            title=note_data.title,
            content=note_data.content,
            created_at=datetime.utcnow()
        )
        self._notes[self._next_id] = note
        self._next_id += 1
        logger.info(f"Created note with id={note.id}")
        return note
    
    def get_note(self, note_id: int) -> Optional[Note]:
        """Get a note by ID."""
        return self._notes.get(note_id)
    
    def list_notes(self) -> list[Note]:
        """List all notes."""
        return list(self._notes.values())
    
    def delete_note(self, note_id: int) -> bool:
        """Delete a note by ID. Returns True if deleted, False if not found."""
        if note_id in self._notes:
            del self._notes[note_id]
            logger.info(f"Deleted note with id={note_id}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all notes (for testing)."""
        self._notes.clear()
        self._next_id = 1


# Global store instance
notes_store = NotesStore()
