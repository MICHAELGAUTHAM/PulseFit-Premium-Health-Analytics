from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.health import HealthRecord
from backend.app.models.users import User
from backend.app.models.goals import Goal
from backend.app.models.notifications import Notification
from backend.app.schemas.health import (
    HealthRecordCreate, HealthRecordUpdate, HealthRecordResponse,
    WaterLogInput, StepsLogInput, CaloriesLogInput, SleepLogInput, BMILogInput
)
from backend.app.services.auth_service import get_current_user
from backend.app.services.achievement_checker import check_and_unlock_achievements

router = APIRouter(tags=["health"])

# Helper: Get or create today's health record for the user
def get_or_create_today_record(user_id: int, db: Session) -> HealthRecord:
    today = date.today()
    record = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.recorded_date == today
    ).first()
    
    if not record:
        # Check if user has height and weight set in their profile
        user = db.query(User).filter(User.id == user_id).first()
        bmi = 0.0
        if user and user.height and user.weight:
            bmi = round(user.weight / ((user.height / 100) ** 2), 1)
            
        record = HealthRecord(
            user_id=user_id,
            recorded_date=today,
            heart_rate=72,  # default baseline
            bmi=bmi
        )
        db.add(record)
        db.commit()
        db.refresh(record)
    return record

@router.get("/dashboard")
def get_dashboard_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. Get today's record
    record = get_or_create_today_record(current_user.id, db)
    
    # 2. Get today's goals
    today = date.today()
    goals = db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.date == today
    ).all()
    
    # If daily goals do not exist, seed defaults
    goal_map = {g.type: g for g in goals}
    defaults = {
        "water": 2500,
        "steps": 10000,
        "calories": 2400,
        "sleep": 8
    }
    
    current_goals = []
    for g_type, default_val in defaults.items():
        if g_type not in goal_map:
            new_goal = Goal(
                user_id=current_user.id,
                type=g_type,
                target_value=default_val,
                completed=False,
                date=today
            )
            db.add(new_goal)
            current_goals.append(new_goal)
        else:
            current_goals.append(goal_map[g_type])
    if len(current_goals) > len(goals):
        db.commit()
    
    # Check goal completion states
    steps_goal = next((g for g in current_goals if g.type == "steps"), None)
    water_goal = next((g for g in current_goals if g.type == "water"), None)
    calories_goal = next((g for g in current_goals if g.type == "calories"), None)
    sleep_goal = next((g for g in current_goals if g.type == "sleep"), None)
    
    # Update completions
    if steps_goal:
        steps_goal.completed = record.steps >= steps_goal.target_value
    if water_goal:
        water_goal.completed = record.water_intake >= water_goal.target_value
    if calories_goal:
        calories_goal.completed = record.calories >= calories_goal.target_value
    if sleep_goal:
        sleep_goal.completed = record.sleep_hours >= sleep_goal.target_value
    
    db.commit()
    
    # Calculate health score: simple weighted average of goal completion
    completed_count = sum(1 for g in current_goals if g.completed)
    # Base index on progress percentages
    progress_sum = 0
    if steps_goal:
        progress_sum += min(100, (record.steps / steps_goal.target_value) * 100)
    if water_goal:
        progress_sum += min(100, (record.water_intake / water_goal.target_value) * 100)
    if calories_goal:
        progress_sum += min(100, (record.calories / calories_goal.target_value) * 100)
    if sleep_goal and record.sleep_hours > 0:
        progress_sum += min(100, (record.sleep_hours / sleep_goal.target_value) * 100)
    else:
        progress_sum += 80  # Default baseline sleep score contribution if sleep not logged
        
    health_score = int(progress_sum / 4)
    
    # Get recent notifications
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).limit(5).all()
    
    return {
        "heart_rate": record.heart_rate,
        "bmi": record.bmi,
        "water_intake": record.water_intake,
        "calories": record.calories,
        "sleep_hours": record.sleep_hours,
        "sleep_score": record.sleep_score,
        "steps": record.steps,
        "health_score": health_score,
        "goals": [
            {
                "type": g.type,
                "target_value": g.target_value,
                "completed": g.completed,
                "progress_pct": min(100, int((record.steps if g.type == "steps" else (record.water_intake if g.type == "water" else (record.calories if g.type == "calories" else record.sleep_hours))) / g.target_value * 100))
            } for g in current_goals
        ],
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.type,
                "is_read": n.is_read,
                "created_at": n.created_at
            } for n in notifications
        ]
    }

@router.post("/health", response_model=HealthRecordResponse)
def add_health_record(record_data: HealthRecordCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    target_date = record_data.recorded_date or date.today()
    
    # Check if record exists
    existing_record = db.query(HealthRecord).filter(
        HealthRecord.user_id == current_user.id,
        HealthRecord.recorded_date == target_date
    ).first()
    
    if existing_record:
        # Update fields
        if record_data.heart_rate is not None:
            existing_record.heart_rate = record_data.heart_rate
        if record_data.bmi is not None:
            existing_record.bmi = record_data.bmi
        if record_data.water_intake is not None:
            existing_record.water_intake = record_data.water_intake
        if record_data.calories is not None:
            existing_record.calories = record_data.calories
        if record_data.sleep_hours is not None:
            existing_record.sleep_hours = record_data.sleep_hours
        if record_data.sleep_score is not None:
            existing_record.sleep_score = record_data.sleep_score
        if record_data.steps is not None:
            existing_record.steps = record_data.steps
        
        db.commit()
        db.refresh(existing_record)
        check_and_unlock_achievements(current_user.id, db)
        return existing_record
        
    new_record = HealthRecord(
        user_id=current_user.id,
        recorded_date=target_date,
        heart_rate=record_data.heart_rate or 72,
        bmi=record_data.bmi or 0.0,
        water_intake=record_data.water_intake or 0,
        calories=record_data.calories or 0,
        sleep_hours=record_data.sleep_hours or 0.0,
        sleep_score=record_data.sleep_score or 0,
        steps=record_data.steps or 0
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    
    check_and_unlock_achievements(current_user.id, db)
    return new_record

@router.get("/health", response_model=List[HealthRecordResponse])
def get_health_records(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(HealthRecord).filter(HealthRecord.user_id == current_user.id).order_by(HealthRecord.recorded_date.desc()).all()

@router.put("/health/{id}", response_model=HealthRecordResponse)
def update_health_record(id: int, record_data: HealthRecordUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.query(HealthRecord).filter(
        HealthRecord.id == id,
        HealthRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Health record not found")
        
    for var, val in vars(record_data).items():
        if val is not None:
            setattr(record, var, val)
            
    db.commit()
    db.refresh(record)
    check_and_unlock_achievements(current_user.id, db)
    return record

@router.delete("/health/{id}")
def delete_health_record(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.query(HealthRecord).filter(
        HealthRecord.id == id,
        HealthRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Health record not found")
        
    db.delete(record)
    db.commit()
    return {"message": "Health record deleted successfully"}

# ----------------- BIOMETRIC LOGGING ROUTES -----------------

@router.post("/water/add")
def add_water(payload: WaterLogInput, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = get_or_create_today_record(current_user.id, db)
    record.water_intake += payload.amount
    db.commit()
    
    # Check achievements
    check_and_unlock_achievements(current_user.id, db)
    return {"water_intake": record.water_intake}

@router.get("/water")
def get_water(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = get_or_create_today_record(current_user.id, db)
    return {"water_intake": record.water_intake}

@router.post("/bmi/calculate")
def calculate_bmi(payload: BMILogInput, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bmi = round(payload.weight / ((payload.height / 100) ** 2), 1)
    
    # Update profile default height/weight
    current_user.height = payload.height
    current_user.weight = payload.weight
    
    # Update today's record bmi
    record = get_or_create_today_record(current_user.id, db)
    record.bmi = bmi
    db.commit()
    return {"bmi": bmi}

@router.post("/sleep")
def add_sleep(payload: SleepLogInput, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = get_or_create_today_record(current_user.id, db)
    record.sleep_hours = payload.hours
    record.sleep_score = payload.score
    db.commit()
    
    check_and_unlock_achievements(current_user.id, db)
    return {"sleep_hours": record.sleep_hours, "sleep_score": record.sleep_score}

@router.get("/sleep")
def get_sleep(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = get_or_create_today_record(current_user.id, db)
    return {"sleep_hours": record.sleep_hours, "sleep_score": record.sleep_score}

@router.post("/calories")
def add_calories(payload: CaloriesLogInput, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = get_or_create_today_record(current_user.id, db)
    record.calories = payload.calories
    db.commit()
    
    check_and_unlock_achievements(current_user.id, db)
    return {"calories": record.calories}

@router.get("/calories")
def get_calories(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = get_or_create_today_record(current_user.id, db)
    return {"calories": record.calories}

@router.post("/steps")
def add_steps(payload: StepsLogInput, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = get_or_create_today_record(current_user.id, db)
    record.steps = payload.steps
    db.commit()
    
    check_and_unlock_achievements(current_user.id, db)
    return {"steps": record.steps}

@router.get("/steps")
def get_steps(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = get_or_create_today_record(current_user.id, db)
    return {"steps": record.steps}
