"""
Messages endpoints for community features.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.core.database import User
from src.api.v1.endpoints.auth import get_current_user

router = APIRouter()


class MessageResponse(BaseModel):
    id: int
    content: str
    sender_id: int
    receiver_id: int
    is_read: bool


@router.get("/", response_model=List[MessageResponse])
async def get_messages(current_user: User = Depends(get_current_user)):
    """Get user's messages."""
    # Stub implementation
    return []


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(message_id: int, current_user: User = Depends(get_current_user)):
    """Get message by ID."""
    # Stub implementation
    raise HTTPException(status_code=404, detail="Message not found")