from datetime import datetime
from enum import Enum

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


class GoalStatus(Enum):
    ACTIVE = "В процессе накопления"
    COMPLETED = "Достигнута"
    CANCELLED = "Отменена"


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
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)

    user = relationship("UserProfile", back_populates="goals")
    account = relationship("Account", back_populates="goals")
    contributions = relationship("GoalContribution", back_populates="goal")


class GoalContribution(Base):
    __tablename__ = "goal_contributions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    contributed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    is_active_pay: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    goal_id: Mapped[int] = mapped_column(Integer, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_profile.id", ondelete="CASCADE"), nullable=False)

    goal = relationship("Goal", back_populates="contributions")
    user = relationship("UserProfile", back_populates="goal_contributions")
