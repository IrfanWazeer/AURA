from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Task, User
from app.dependencies import get_current_user
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    status_filter: Optional[str] = None,
    priority_filter: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all tasks belonging to the authenticated user with optional status and priority filters.
    """
    query = select(Task).where(Task.user_id == current_user.id)
    
    if status_filter:
        query = query.where(Task.status == status_filter)
    if priority_filter:
        query = query.where(Task.priority == str(priority_filter)) # Cast based on models.py choice

    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new task pinned to the current authenticated user.
    """
    db_task = Task(
        title=task_in.title,
        # If your base models.py doesn't have a description field, 
        # it will be kept locally or safely omitted dynamically.
        user_id=current_user.id,
        priority=str(task_in.priority),
        status="todo",
        deadline=task_in.deadline,
        estimated_mins=task_in.estimated_mins
    )
    
    # Check if model has optional description column
    if hasattr(db_task, 'description'):
        setattr(db_task, 'description', task_in.description)

    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


@router.get("/{id}", response_model=TaskResponse)
async def get_task(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a single specific task by its UUID.
    """
    result = await db.execute(select(Task).where(Task.id == id, Task.user_id == current_user.id))
    task = result.scalars().first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied."
        )
    return task


@router.patch("/{id}", response_model=TaskResponse)
async def update_task(
    id: uuid.UUID,
    task_in: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Partially update task fields dynamically.
    """
    result = await db.execute(select(Task).where(Task.id == id, Task.user_id == current_user.id))
    task = result.scalars().first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied."
        )

    # Convert schema payload to a dict while removing explicitly unset attributes
    update_data = task_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "priority" and value is not None:
            setattr(task, field, str(value))
        else:
            setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Permanently delete a task.
    """
    result = await db.execute(select(Task).where(Task.id == id, Task.user_id == current_user.id))
    task = result.scalars().first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied."
        )

    await db.delete(task)
    await db.commit()
    return None


@router.post("/{id}/complete", response_model=TaskResponse)
async def complete_task(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Quick endpoint action targeting a specific task status to modify it to 'done'.
    """
    result = await db.execute(select(Task).where(Task.id == id, Task.user_id == current_user.id))
    task = result.scalars().first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied."
        )

    task.status = "done"
    await db.commit()
    await db.refresh(task)
    return task