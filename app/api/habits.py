from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Habit, User
from app.dependencies import get_current_user
from app.schemas.habit import HabitCreate, HabitUpdate, HabitResponse

router = APIRouter(prefix="/habits", tags=["Habits"])


@router.get("", response_model=List[HabitResponse])
async def list_habits(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Habit).where(Habit.user_id == current_user.id))
    return result.scalars().all()


@router.post("", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit(
    habit_in: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_habit = Habit(
        user_id=current_user.id,
        title=habit_in.title,
        frequency=habit_in.frequency,
        current_streak=0
    )
    db.add(db_habit)
    await db.commit()
    await db.refresh(db_habit)
    return db_habit


@router.patch("/{id}", response_model=HabitResponse)
async def update_habit(
    id: uuid.UUID,
    habit_in: HabitUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Habit).where(Habit.id == id, Habit.user_id == current_user.id))
    habit = result.scalars().first()
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")

    update_data = habit_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(habit, field, value)

    await db.commit()
    await db.refresh(habit)
    return habit


@router.post("/{id}/complete", response_model=HabitResponse)
async def track_habit_completion(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Increment current_streak by 1 whenever habit is checked-off.
    """
    result = await db.execute(select(Habit).where(Habit.id == id, Habit.user_id == current_user.id))
    habit = result.scalars().first()
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")

    habit.current_streak += 1
    await db.commit()
    await db.refresh(habit)
    return habit


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Habit).where(Habit.id == id, Habit.user_id == current_user.id))
    habit = result.scalars().first()
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")

    await db.delete(habit)
    await db.commit()
    return None