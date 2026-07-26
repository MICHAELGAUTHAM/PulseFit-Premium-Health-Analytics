from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from backend.app.models.achievements import Achievement
from backend.app.models.notifications import Notification
from backend.app.models.health import HealthRecord

def check_and_unlock_achievements(user_id: int, db: Session):
    unlocked_any = False
    
    def unlock_badge(badge_name: str, title: str, desc: str) -> bool:
        existing = db.query(Achievement).filter(
            Achievement.user_id == user_id,
            Achievement.badge_name == badge_name
        ).first()
        if not existing:
            achievement = Achievement(user_id=user_id, badge_name=badge_name)
            db.add(achievement)
            
            notification = Notification(
                user_id=user_id,
                title=f"🏆 Achievement Unlocked: {title}",
                message=desc,
                type="achievement_unlocked"
            )
            db.add(notification)
            return True
        return False

    # 1. First Login (Automatic unlock)
    if unlock_badge("first_login", "First Step", "Welcome to PulseFit! You completed your first login."):
        unlocked_any = True

    # Query today's health record
    today = date.today()
    record = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.recorded_date == today
    ).first()

    if record:
        # 2. Hydration Master (Goal: 2500ml)
        if record.water_intake >= 2500:
            if unlock_badge("hydration_master", "Hydration Master", "You reached your daily hydration target of 2.5L!"):
                unlocked_any = True

        # 3. Step Champion (Goal: 10000 steps)
        if record.steps >= 10000:
            if unlock_badge("step_champion", "Step Champion", "You walked 10,000 steps or more today!"):
                unlocked_any = True

        # 4. Healthy Sleeper (Score >= 90%)
        if record.sleep_score >= 90:
            if unlock_badge("healthy_sleeper", "Healthy Sleeper", "You achieved a sleep quality score of 90% or higher!"):
                unlocked_any = True

        # 5. Goal Crusher (steps, water, calories all met)
        if record.steps >= 10000 and record.water_intake >= 2500 and record.calories >= 2400:
            if unlock_badge("goal_crusher", "Goal Crusher", "Amazing! You crushed all your daily goals today."):
                unlocked_any = True

    # 6. 7-Day Streak
    recent_records = db.query(HealthRecord.recorded_date).filter(
        HealthRecord.user_id == user_id
    ).order_by(HealthRecord.recorded_date.asc()).all()
    
    unique_dates = [r[0] for r in recent_records]
    if len(unique_dates) >= 7:
        consecutive_count = 1
        has_streak = False
        for i in range(1, len(unique_dates)):
            if unique_dates[i] - unique_dates[i-1] == timedelta(days=1):
                consecutive_count += 1
                if consecutive_count >= 7:
                    has_streak = True
                    break
            else:
                consecutive_count = 1
        
        if has_streak:
            if unlock_badge("streak_7", "7-Day Streak", "Sensational! You logged health metrics for 7 consecutive days."):
                unlocked_any = True

    if unlocked_any:
        db.commit()
