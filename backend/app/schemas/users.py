from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)
    gender: Optional[str] = None
    age: Optional[int] = Field(None, ge=0)
    height: Optional[float] = Field(None, ge=0)  # in cm
    weight: Optional[float] = Field(None, ge=0)  # in kg

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = Field(None, ge=0)
    height: Optional[float] = Field(None, ge=0)
    weight: Optional[float] = Field(None, ge=0)

class UserResponse(UserBase):
    id: int
    gender: Optional[str]
    age: Optional[int]
    height: Optional[float]
    weight: Optional[float]
    profile_pic: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)
