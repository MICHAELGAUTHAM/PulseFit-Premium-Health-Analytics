from backend.app.schemas.users import UserCreate, UserUpdate, UserResponse, PasswordChange
from backend.app.schemas.health import HealthRecordCreate, HealthRecordUpdate, HealthRecordResponse, WaterLogInput, StepsLogInput, CaloriesLogInput, SleepLogInput, BMILogInput
from backend.app.schemas.goals import GoalCreate, GoalUpdate, GoalResponse
from backend.app.schemas.achievements import AchievementResponse
from backend.app.schemas.notifications import NotificationResponse, NotificationUpdate
from backend.app.schemas.auth import LoginRequest, Token, TokenData, ForgotPasswordRequest, VerifyOTPRequest, ResetPasswordRequest
