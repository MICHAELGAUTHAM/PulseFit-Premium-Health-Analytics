from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.goals import Goal
from backend.app.models.users import User
from backend.app.schemas.goals import GoalResponse, GoalUpdate, GoalCreate
from backend.app.services.auth_service import get_current_user

router = APIRouter(prefix="/goals", tags=["goals"])

@router.get("", response_model=List[GoalResponse])
def get_goals(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = date.today()
    goals = db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.date == today
    ).all()
    
    # If daily goals do not exist, create defaults
    if not goals:
        defaults = {
            "water": 2500,
            "steps": 10000,
            "calories": 2400,
            "sleep": 8
        }
        goals = []
        for g_type, default_val in defaults.items():
            new_goal = Goal(
                user_id=current_user.id,
                type=g_type,
                target_value=default_val,
                completed=False,
                date=today
            )
            db.add(new_goal)
            goals.append(new_goal)
        db.commit()
        for g in goals:
            db.refresh(g)
            
    return goals

@router.put("/{type}", response_model=GoalResponse)
def update_goal_by_type(type: str, payload: GoalUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = date.today()
    goal = db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.type == type,
        Goal.date == today
    ).first()
    
    if not goal:
        # Create goal if it does not exist for today
        goal = Goal(
            user_id=current_user.id,
            type=type,
            target_value=payload.target_value or 1000.0,
            completed=payload.completed or False,
            date=today
        )
        db.add(goal)
    else:
        if payload.target_value is not None:
            goal.target_value = payload.target_value
        if payload.completed is not None:
            goal.completed = payload.completed
            
    db.commit()
    db.refresh(goal)
    return goal
