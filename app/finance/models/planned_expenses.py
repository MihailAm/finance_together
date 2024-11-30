from datetime import datetime
from enum import Enum

from sqlalchemy import Integer, Float, String, DateTime, ForeignKey
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship

from app.infrastructure.database import Base


class PlannedExpenseType(str, Enum):
    INCOME = "доход"
    EXPENSE = "расход"


class PlannedExpenses(Base):
    __tablename__ = "planned_expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    dur_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    type: Mapped[PlannedExpenseType] = mapped_column(SQLAlchemyEnum(PlannedExpenseType), nullable=False)

    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("groups.id"), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_profile.id"), nullable=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'), nullable=False)

    # user = relationship("UserProfile", back_populates="planned_expenses")
    # group = relationship("Group", back_populates="planned_expenses")

    @validates("user_id", "group_id")
    def validate_user_or_group(self, key, value):
        if key == "user_id" and value is not None and self.group_id is not None:
            raise ValueError("Планирование не может быть и персональным и групповым.")
        if key == "group_id" and value is not None and self.user_id is not None:
            raise ValueError("Планирование не может быть и персональным и групповым.")
        return value

