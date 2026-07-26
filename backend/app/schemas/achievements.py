from pydantic import BaseModel
from datetime import datetime

class AchievementResponse(BaseModel):
    id: int
    user_id: int
    badge_name: str
    unlocked_at: datetime

    class Config:
        from_attributes = True
