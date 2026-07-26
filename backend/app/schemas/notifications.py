from pydantic import BaseModel
from datetime import datetime

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: str  # "water_reminder", "goal_completed", etc.
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationUpdate(BaseModel):
    is_read: bool
