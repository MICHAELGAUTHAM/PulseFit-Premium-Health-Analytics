import os
import shutil
import random
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.users import User
from backend.app.models.auth import PasswordResetOTP, UserSession
from backend.app.schemas.auth import LoginRequest, Token, ForgotPasswordRequest, VerifyOTPRequest, ResetPasswordRequest
from backend.app.schemas.users import UserCreate, UserUpdate, UserResponse, PasswordChange
from backend.app.services.auth_service import get_password_hash, verify_password, create_access_token, get_current_user, oauth2_scheme

router = APIRouter(prefix="/auth", tags=["auth"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if user_data.password != user_data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_pwd = get_password_hash(user_data.password)
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hashed_pwd,
        gender=user_data.gender,
        age=user_data.age,
        height=user_data.height,
        weight=user_data.weight
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    expiry_days = 30 if login_data.remember_me else 1
    expires_delta = timedelta(days=expiry_days)
    
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=expires_delta)
    
    session_record = UserSession(
        user_id=user.id,
        token=access_token,
        expires_at=datetime.utcnow() + expires_delta
    )
    db.add(session_record)
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    session_record = db.query(UserSession).filter(UserSession.token == token).first()
    if session_record:
        db.delete(session_record)
        db.commit()
    return {"message": "Logged out successfully"}

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with this email does not exist")
    
    # Generate 6-digit OTP
    otp_code = f"{random.randint(100000, 999999)}"
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    # Invalidate any old OTPs for this email
    db.query(PasswordResetOTP).filter(PasswordResetOTP.email == req.email).delete()
    
    otp_record = PasswordResetOTP(
        email=req.email,
        otp_code=otp_code,
        expires_at=expires_at,
        is_verified=False
    )
    db.add(otp_record)
    db.commit()
    
    # Mocking email delivery by returning OTP in response for local testing
    print(f"PASSWORD RESET OTP FOR {req.email}: {otp_code}")
    return {"message": "OTP sent successfully to email", "otp_code": otp_code}

@router.post("/verify-otp")
def verify_otp(req: VerifyOTPRequest, db: Session = Depends(get_db)):
    record = db.query(PasswordResetOTP).filter(
        PasswordResetOTP.email == req.email,
        PasswordResetOTP.otp_code == req.otp_code
    ).first()
    
    if not record:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
    
    if record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP code has expired")
        
    record.is_verified = True
    db.commit()
    return {"message": "OTP verified successfully"}

@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    if req.new_password != req.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
        
    otp_record = db.query(PasswordResetOTP).filter(
        PasswordResetOTP.email == req.email,
        PasswordResetOTP.otp_code == req.otp_code,
        PasswordResetOTP.is_verified == True
    ).first()
    
    if not otp_record:
        raise HTTPException(status_code=400, detail="OTP must be verified first")
        
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.hashed_password = get_password_hash(req.new_password)
    
    # Revoke sessions for security
    db.query(UserSession).filter(UserSession.user_id == user.id).delete()
    # Delete the OTP record
    db.delete(otp_record)
    db.commit()
    
    return {"message": "Password reset successfully"}

@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_profile(profile_data: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name
    if profile_data.gender is not None:
        current_user.gender = profile_data.gender
    if profile_data.age is not None:
        current_user.age = profile_data.age
    if profile_data.height is not None:
        current_user.height = profile_data.height
    if profile_data.weight is not None:
        current_user.weight = profile_data.weight
        
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/profile/avatar")
def upload_avatar(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # File validation
    filename, ext = os.path.splitext(file.filename)
    ext = ext.lower()
    if ext not in [".jpg", ".jpeg", ".png", ".gif"]:
        raise HTTPException(status_code=400, detail="Only JPG, JPEG, PNG, and GIF files are allowed")
        
    # Safe naming
    new_filename = f"user_{current_user.id}_avatar{ext}"
    dest_path = os.path.join(UPLOAD_DIR, new_filename)
    
    try:
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
    current_user.profile_pic = f"/uploads/{new_filename}"
    db.commit()
    
    return {"message": "Avatar uploaded successfully", "profile_pic": current_user.profile_pic}

@router.post("/profile/change-password")
def change_password(req: PasswordChange, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(req.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    if req.new_password != req.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
        
    current_user.hashed_password = get_password_hash(req.new_password)
    db.commit()
    return {"message": "Password changed successfully"}

@router.delete("/profile/delete-account")
def delete_account(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted successfully"}

@router.get("/users", response_model=List[UserResponse])
def list_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id.desc()).all()
    return users

@router.post("/users", response_model=UserResponse)
def create_user_by_admin(user_data: UserCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_data.password != user_data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_pwd = get_password_hash(user_data.password)
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hashed_pwd,
        gender=user_data.gender,
        age=user_data.age,
        height=user_data.height,
        weight=user_data.weight
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
