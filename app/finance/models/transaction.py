from datetime import datetime
from enum import Enum

from sqlalchemy import Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Enum as SQLAlchemyEnum

from app.infrastructure.database import Base


class TransactionType(str, Enum):
    INCOME = "доход"
    EXPENSE = "расход"


class FinanceTransaction(Base):
    __tablename__ = "finance_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    transaction_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    type: Mapped[TransactionType] = mapped_column(SQLAlchemyEnum(TransactionType), nullable=False)

    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_profile.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    account = relationship("Account", back_populates="transactions")
    user = relationship("UserProfile", back_populates="transactions")
