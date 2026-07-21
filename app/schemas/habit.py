from typing import Optional
import uuid
from pydantic import BaseModel, Field, ConfigDict


class HabitBase(BaseModel):
    title: str = Field(..., max_length=255, description="Habit title")
    frequency: str = Field("daily", description="e.g. daily, weekly, 3x_week")


class HabitCreate(HabitBase):
    pass


class HabitUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    frequency: Optional[str] = None


class HabitResponse(HabitBase):
    id: uuid.UUID
    user_id: uuid.UUID
    current_streak: int

    model_config = ConfigDict(from_attributes=True)