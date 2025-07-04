"""
AI Companions endpoints for community features.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.core.database import User
from src.api.v1.endpoints.auth import get_current_user

router = APIRouter()


class AICompanionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    model_type: str
    is_public: bool
    interaction_count: int


@router.get("/", response_model=List[AICompanionResponse])
async def get_ai_companions(current_user: User = Depends(get_current_user)):
    """Get list of AI companions."""
    # Stub implementation
    return []


@router.get("/{companion_id}", response_model=AICompanionResponse)
async def get_ai_companion(companion_id: int, current_user: User = Depends(get_current_user)):
    """Get AI companion by ID."""
    # Stub implementation
    raise HTTPException(status_code=404, detail="AI Companion not found")