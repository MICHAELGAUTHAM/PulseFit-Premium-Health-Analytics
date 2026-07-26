from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import date
from backend.app.database import Base

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)  # "water", "steps", "calories", "sleep"
    target_value = Column(Float, nullable=False)
    completed = Column(Boolean, default=False)
    date = Column(Date, default=date.today, nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'type', 'date', name='uq_user_goal_type_date'),
    )

    user = relationship("User", back_populates="goals")
