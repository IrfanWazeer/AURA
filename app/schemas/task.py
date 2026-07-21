from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, Field, ConfigDict


class TaskBase(BaseModel):
    title: str = Field(..., max_length=255, description="The title of the task")
    description: Optional[str] = Field(None, description="Detailed task description")
    priority: int = Field(2, ge=1, le=4, description="Priority level where 1=Highest, 4=Lowest")
    deadline: Optional[datetime] = Field(None, description="Task deadline in ISO layout")
    estimated_mins: Optional[int] = Field(None, ge=0, description="Estimated time in minutes")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=4)
    status: Optional[str] = Field(None, description="e.g., todo, in_progress, done")
    deadline: Optional[datetime] = None
    estimated_mins: Optional[int] = Field(None, ge=0)


class TaskResponse(TaskBase):
    id: uuid.UUID
    status: str
    user_id: uuid.UUID
    created_at: datetime

    # Pydantic v2 setup for automatic ORM attribute parsing
    model_config = ConfigDict(from_attributes=True)