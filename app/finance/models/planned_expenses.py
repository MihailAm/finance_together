from datetime import datetime
from enum import Enum

from sqlalchemy import Integer, Float, String, DateTime, ForeignKey, Boolean
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship

from app.infrastructure.database import Base


class PlannedExpenseType(str, Enum):
    INCOME = "доход"
    EXPENSE = "расход"


class PlannedExpenses(Base):
    __tablename__ = "planned_expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    dur_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    type: Mapped[PlannedExpenseType] = mapped_column(SQLAlchemyEnum(PlannedExpenseType), nullable=False)
    is_active_pay: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_profile.id", ondelete="CASCADE"), nullable=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'), nullable=False)

    user = relationship("UserProfile", back_populates="planned_expenses")
    account = relationship("Account", back_populates="planned_expenses")
