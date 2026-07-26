from sqlalchemy import Column, Integer, Float, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import date
from backend.app.database import Base

class HealthRecord(Base):
    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    heart_rate = Column(Integer, default=72)
    bmi = Column(Float, default=0.0)
    water_intake = Column(Integer, default=0)  # in ml
    calories = Column(Integer, default=0)      # in kcal
    sleep_hours = Column(Float, default=0.0)   # in hours
    sleep_score = Column(Integer, default=0)   # quality score out of 100
    steps = Column(Integer, default=0)
    recorded_date = Column(Date, default=date.today, nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'recorded_date', name='uq_user_date'),
    )

    user = relationship("User", back_populates="health_records")
