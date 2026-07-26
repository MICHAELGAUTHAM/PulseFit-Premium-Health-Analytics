from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.achievements import Achievement
from backend.app.models.users import User
from backend.app.services.auth_service import get_current_user

router = APIRouter(prefix="/achievements", tags=["achievements"])

@router.get("")
def get_achievements(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    unlocked = db.query(Achievement).filter(Achievement.user_id == current_user.id).all()
    unlocked_names = {a.badge_name for a in unlocked}
    
    # Pre-defined list of system achievements
    all_badges = [
        {
            "id": "first_login",
            "name": "First Step",
            "description": "Log in for the first time.",
            "icon": "zap",
            "color": "var(--secondary-color)"
        },
        {
            "id": "streak_7",
            "name": "7-Day Streak",
            "description": "Log biometrics for 7 consecutive days.",
            "icon": "trophy",
            "color": "var(--warning-color)"
        },
        {
            "id": "hydration_master",
            "name": "Hydro Master",
            "description": "Reach your hydration goal of 2500ml.",
            "icon": "droplet",
            "color": "var(--primary-color)"
        },
        {
            "id": "step_champion",
            "name": "10k Steps",
            "description": "Complete 10,000 steps in a single day.",
            "icon": "footprints",
            "color": "var(--accent-color)"
        },
        {
            "id": "healthy_sleeper",
            "name": "Dreamer",
            "description": "Reach a sleep quality score of 90% or higher.",
            "icon": "moon",
            "color": "var(--secondary-color)"
        },
        {
            "id": "goal_crusher",
            "name": "Goal Crusher",
            "description": "Exceed water, step, and calorie targets today.",
            "icon": "target",
            "color": "var(--success-color)"
        }
    ]
    
    response = []
    for badge in all_badges:
        is_unlocked = badge["id"] in unlocked_names
        unlocked_record = next((a for a in unlocked if a.badge_name == badge["id"]), None)
        response.append({
            "badge_id": badge["id"],
            "name": badge["name"],
            "description": badge["description"],
            "icon": badge["icon"],
            "color": badge["color"],
            "unlocked": is_unlocked,
            "unlocked_at": unlocked_record.unlocked_at if is_unlocked and unlocked_record else None
        })
        
    return response
