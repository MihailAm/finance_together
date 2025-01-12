from datetime import datetime
from enum import Enum

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.infrastructure.database import Base


class GoalStatus(Enum):
    ACTIVE = "В процессе накопления"  # Цель в процессе накопления
    COMPLETED = "Достигнута"  # Цель достигнута
    CANCELLED = "Отменена"  # Цель отменена


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    target_amount: Mapped[float] = mapped_column(Float, nullable=False)
    current_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    status: Mapped[GoalStatus] = mapped_column(SQLAlchemyEnum(GoalStatus), default=GoalStatus.ACTIVE, nullable=False)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_profile.id", ondelete="CASCADE"), nullable=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=True)

    user = relationship("UserProfile", back_populates="goals")
    group = relationship("Group", back_populates="goals")

    @validates("user_id", "group_id")
    def validate_user_or_group(self, key, value):
        if key == "user_id" and value is not None and self.group_id is not None:
            raise ValueError("Цель не может быть и персональным и групповым.")
        if key == "group_id" and value is not None and self.user_id is not None:
            raise ValueError("Цель не может быть и персональным и групповым.")
        return value
