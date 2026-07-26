from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class GoalBase(BaseModel):
    type: str  # "water", "steps", "calories", "sleep"
    target_value: float = Field(..., gt=0)
    completed: Optional[bool] = False
    date: Optional[date] = None

class GoalCreate(BaseModel):
    type: str
    target_value: float = Field(..., gt=0)
    date: Optional[date] = None

class GoalUpdate(BaseModel):
    target_value: Optional[float] = Field(None, gt=0)
    completed: Optional[bool] = None

class GoalResponse(GoalBase):
    id: int
    user_id: int
    date: date

    class Config:
        from_attributes = True
