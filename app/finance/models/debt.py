from datetime import datetime
from enum import Enum

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


class DebtStatus(Enum):
    PENDING = "Ожидает возврата"
    PAID = "Выплачено"
    CANCELLED = "Отменено"


class Debt(Base):
    __tablename__ = "debts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[DebtStatus] = mapped_column(SQLAlchemyEnum(DebtStatus), default=DebtStatus.PENDING, nullable=False)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_profile.id"), nullable=True)

    user = relationship("UserProfile", back_populates="debts")