from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, Field, ConfigDict


class GoalBase(BaseModel):
    title: str = Field(..., max_length=255, description="Goal title")
    category: Optional[str] = Field(None, max_length=100, description="Category e.g. Career, Health, Finance")
    target_date: Optional[datetime] = Field(None, description="Target completion date")


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = None
    target_date: Optional[datetime] = None
    progress: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage (0-100)")
    status: Optional[str] = Field(None, description="e.g. active, achieved, paused")


class GoalResponse(GoalBase):
    id: uuid.UUID
    user_id: uuid.UUID
    progress: int
    status: str

    model_config = ConfigDict(from_attributes=True)