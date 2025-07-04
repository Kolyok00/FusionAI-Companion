"""
Posts endpoints for community features.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.core.database import User
from src.api.v1.endpoints.auth import get_current_user

router = APIRouter()


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    upvotes: int
    downvotes: int
    comment_count: int


@router.get("/", response_model=List[PostResponse])
async def get_posts(current_user: User = Depends(get_current_user)):
    """Get list of posts."""
    # Stub implementation
    return []


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, current_user: User = Depends(get_current_user)):
    """Get post by ID."""
    # Stub implementation
    raise HTTPException(status_code=404, detail="Post not found")