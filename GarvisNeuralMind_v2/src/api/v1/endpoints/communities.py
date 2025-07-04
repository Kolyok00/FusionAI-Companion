"""
Communities endpoints for community features.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.core.database import User
from src.api.v1.endpoints.auth import get_current_user

router = APIRouter()


class CommunityResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    avatar_url: Optional[str]
    member_count: int
    is_public: bool


@router.get("/", response_model=List[CommunityResponse])
async def get_communities(current_user: User = Depends(get_current_user)):
    """Get list of communities."""
    # Stub implementation
    return []


@router.get("/{community_id}", response_model=CommunityResponse)
async def get_community(community_id: int, current_user: User = Depends(get_current_user)):
    """Get community by ID."""
    # Stub implementation
    raise HTTPException(status_code=404, detail="Community not found")