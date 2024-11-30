from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.finance.models import FinanceTransaction
from app.infrastructure.database import Base


class UserProfile(Base):
    __tablename__ = "user_profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    surname: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    google_access_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    yandex_access_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    password: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # account = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    # transactions = relationship("FinanceTransaction", back_populates="user", cascade="all, delete-orphan")
    # goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    # debts = relationship("Debt", back_populates="user", cascade="all, delete-orphan")
    # planned_expenses = relationship("PlannedExpenses", back_populates='user', cascade="all, delete-orphan")
    # category = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    #
    # group_associations = relationship("GroupMember", back_populates="user")
    # groups = relationship("Group", secondary="group_members", back_populates="members")
