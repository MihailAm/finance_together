from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.infrastructure.database import Base
from app.groups.models.group import Group
from app.users.models.user import UserProfile


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_name: Mapped[str] = mapped_column(String, nullable=False)
    balance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("user_profile.id"), nullable=True, default=None)
    group_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("groups.id"), nullable=True, default=None, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    @validates("user_id", "group_id")
    def validate_user_or_group(self, key, value):
        if key == "user_id" and value is not None and self.group_id is not None:
            raise ValueError("Аккаунт не может быть и персональным и групповым.")
        if key == "group_id" and value is not None and self.user_id is not None:
            raise ValueError("Аккаунт не может быть и персональным и групповым.")
        return value
