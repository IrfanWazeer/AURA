from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Goal, User
from app.dependencies import get_current_user
from app.schemas.goal import GoalCreate, GoalUpdate, GoalResponse

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.get("", response_model=List[GoalResponse])
async def list_goals(
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Goal).where(Goal.user_id == current_user.id)
    if category:
        query = query.where(Goal.category == category)
    if status_filter:
        query = query.where(Goal.status == status_filter)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_in: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_goal = Goal(
        user_id=current_user.id,
        title=goal_in.title,
        category=goal_in.category,
        target_date=goal_in.target_date,
        progress=0,
        status="active"
    )
    db.add(db_goal)
    await db.commit()
    await db.refresh(db_goal)
    return db_goal


@router.get("/{id}", response_model=GoalResponse)
async def get_goal(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Goal).where(Goal.id == id, Goal.user_id == current_user.id))
    goal = result.scalars().first()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return goal


@router.patch("/{id}", response_model=GoalResponse)
async def update_goal(
    id: uuid.UUID,
    goal_in: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Goal).where(Goal.id == id, Goal.user_id == current_user.id))
    goal = result.scalars().first()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    update_data = goal_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)

    await db.commit()
    await db.refresh(goal)
    return goal


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Goal).where(Goal.id == id, Goal.user_id == current_user.id))
    goal = result.scalars().first()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    await db.delete(goal)
    await db.commit()
    return None