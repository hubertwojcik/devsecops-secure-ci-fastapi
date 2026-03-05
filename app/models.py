"""Pydantic models for the Notes API."""

from datetime import datetime
from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    """Model for creating a new note."""
    
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., max_length=5000)


class Note(BaseModel):
    """Model representing a note."""
    
    id: int
    title: str
    content: str
    created_at: datetime


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str
