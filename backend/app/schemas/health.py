from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class HealthRecordBase(BaseModel):
    heart_rate: Optional[int] = Field(None, ge=30, le=220)
    bmi: Optional[float] = Field(None, ge=0)
    water_intake: Optional[int] = Field(None, ge=0)  # in ml
    calories: Optional[int] = Field(None, ge=0)      # in kcal
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    sleep_score: Optional[int] = Field(None, ge=0, le=100)
    steps: Optional[int] = Field(None, ge=0)

class HealthRecordCreate(HealthRecordBase):
    recorded_date: Optional[date] = None

class HealthRecordUpdate(HealthRecordBase):
    pass

class HealthRecordResponse(HealthRecordBase):
    id: int
    user_id: int
    recorded_date: date

    class Config:
        from_attributes = True

# Custom tracker payload schemas
class WaterLogInput(BaseModel):
    amount: int = Field(..., gt=0)  # ml to add

class StepsLogInput(BaseModel):
    steps: int = Field(..., ge=0)

class CaloriesLogInput(BaseModel):
    calories: int = Field(..., ge=0)

class SleepLogInput(BaseModel):
    hours: float = Field(..., ge=0, le=24)
    score: int = Field(..., ge=0, le=100)

class BMILogInput(BaseModel):
    height: float = Field(..., gt=0)  # cm
    weight: float = Field(..., gt=0)  # kg
