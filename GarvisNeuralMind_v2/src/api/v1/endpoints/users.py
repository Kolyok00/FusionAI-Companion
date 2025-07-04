"""
Users endpoints for community features.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.core.database import User
from src.api.v1.endpoints.auth import get_current_user

router = APIRouter()


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    reputation_score: int
    level: int
    is_verified: bool


@router.get("/", response_model=List[UserResponse])
async def get_users(current_user: User = Depends(get_current_user)):
    """Get list of users."""
    # Stub implementation
    return []


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, current_user: User = Depends(get_current_user)):
    """Get user by ID."""
    # Stub implementation
    raise HTTPException(status_code=404, detail="User not found")