from datetime import date, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.health import HealthRecord
from backend.app.models.users import User
from backend.app.services.auth_service import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Helper: compute a health index score out of 100 for a record
def calculate_score(record: HealthRecord) -> int:
    # Steps (out of 10k), Water (out of 2.5L), Calories (out of 2.4k), Sleep (out of 8h)
    s_pct = min(100, (record.steps / 10000) * 100)
    w_pct = min(100, (record.water_intake / 2500) * 100)
    c_pct = min(100, (record.calories / 2400) * 100)
    sl_pct = min(100, (record.sleep_hours / 8) * 100) if record.sleep_hours > 0 else 80
    return int((s_pct + w_pct + c_pct + sl_pct) / 4)

@router.get("/weekly")
def get_weekly_analytics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = date.today()
    start_date = today - timedelta(days=6)
    
    # Query database
    records = db.query(HealthRecord).filter(
        HealthRecord.user_id == current_user.id,
        HealthRecord.recorded_date >= start_date,
        HealthRecord.recorded_date <= today
    ).all()
    
    record_map = {r.recorded_date: r for r in records}
    
    # Return exactly 7 days
    labels = []
    steps = []
    calories = []
    water = []
    sleep = []
    heart_rate = []
    health_score = []
    activity = [] # calculated activity score (based on steps/calories)
    
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    for i in range(7):
        day = start_date + timedelta(days=i)
        weekday_label = weekdays[day.weekday()]
        labels.append(f"{weekday_label} ({day.strftime('%m/%d')})")
        
        record = record_map.get(day)
        if record:
            steps.append(record.steps)
            calories.append(record.calories)
            water.append(record.water_intake)
            sleep.append(record.sleep_hours)
            heart_rate.append(record.heart_rate)
            h_score = calculate_score(record)
            health_score.append(h_score)
            activity.append(min(100, int((record.steps / 10000) * 50 + (record.calories / 2400) * 50)))
        else:
            # Seed default values for missing dates
            steps.append(0)
            calories.append(0)
            water.append(0)
            sleep.append(0.0)
            heart_rate.append(72)
            health_score.append(50)
            activity.append(0)
            
    return {
        "labels": labels,
        "steps": steps,
        "calories": calories,
        "water": water,
        "sleep": sleep,
        "heart_rate": heart_rate,
        "health_score": health_score,
        "activity": activity
    }

@router.get("/monthly")
def get_monthly_analytics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = date.today()
    start_date = today - timedelta(days=29)
    
    records = db.query(HealthRecord).filter(
        HealthRecord.user_id == current_user.id,
        HealthRecord.recorded_date >= start_date,
        HealthRecord.recorded_date <= today
    ).all()
    
    record_map = {r.recorded_date: r for r in records}
    
    labels = []
    steps = []
    calories = []
    water = []
    sleep = []
    heart_rate = []
    health_score = []
    
    for i in range(30):
        day = start_date + timedelta(days=i)
        labels.append(day.strftime("%b %d"))
        
        record = record_map.get(day)
        if record:
            steps.append(record.steps)
            calories.append(record.calories)
            water.append(record.water_intake)
            sleep.append(record.sleep_hours)
            heart_rate.append(record.heart_rate)
            health_score.append(calculate_score(record))
        else:
            steps.append(0)
            calories.append(0)
            water.append(0)
            sleep.append(0.0)
            heart_rate.append(72)
            health_score.append(0)
            
    return {
        "labels": labels,
        "steps": steps,
        "calories": calories,
        "water": water,
        "sleep": sleep,
        "heart_rate": heart_rate,
        "health_score": health_score
    }

@router.get("/yearly")
def get_yearly_analytics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Group by past 12 months
    today = date.today()
    start_date = date(today.year - 1, today.month, 1) + timedelta(days=32) # roughly 11 months ago, start of month
    start_date = date(start_date.year, start_date.month, 1)
    
    records = db.query(HealthRecord).filter(
        HealthRecord.user_id == current_user.id,
        HealthRecord.recorded_date >= start_date,
        HealthRecord.recorded_date <= today
    ).all()
    
    # Group by year-month
    grouped: Dict[str, List[HealthRecord]] = {}
    current_day = start_date
    while current_day <= today:
        key = current_day.strftime("%Y-%m")
        grouped[key] = []
        # Move to next month
        if current_day.month == 12:
            current_day = date(current_day.year + 1, 1, 1)
        else:
            current_day = date(current_day.year, current_day.month + 1, 1)
            
    for record in records:
        key = record.recorded_date.strftime("%Y-%m")
        if key in grouped:
            grouped[key].append(record)
            
    labels = []
    steps_avg = []
    calories_sum = []
    water_avg = []
    sleep_avg = []
    heart_rate_avg = []
    health_score_avg = []
    
    for key in sorted(grouped.keys()):
        dt = datetime.strptime(key, "%Y-%m")
        labels.append(dt.strftime("%b %Y"))
        
        month_records = grouped[key]
        if month_records:
            steps_avg.append(int(sum(r.steps for r in month_records) / len(month_records)))
            calories_sum.append(int(sum(r.calories for r in month_records)))
            water_avg.append(int(sum(r.water_intake for r in month_records) / len(month_records)))
            sleep_avg.append(round(sum(r.sleep_hours for r in month_records) / len(month_records), 1))
            heart_rate_avg.append(int(sum(r.heart_rate for r in month_records) / len(month_records)))
            health_score_avg.append(int(sum(calculate_score(r) for r in month_records) / len(month_records)))
        else:
            steps_avg.append(0)
            calories_sum.append(0)
            water_avg.append(0)
            sleep_avg.append(0.0)
            heart_rate_avg.append(72)
            health_score_avg.append(0)
            
    return {
        "labels": labels,
        "steps": steps_avg,
        "calories": calories_sum,
        "water": water_avg,
        "sleep": sleep_avg,
        "heart_rate": heart_rate_avg,
        "health_score": health_score_avg
    }
