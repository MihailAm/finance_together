from datetime import datetime

from sqlalchemy import Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.infrastructure.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_name: Mapped[str] = mapped_column(String, nullable=False)
    balance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_profile.id"), nullable=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("groups.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # user = relationship("UserProfile", back_populates="account")
    # transactions = relationship("FinanceTransaction", back_populates="account")
    # group = relationship("Group", back_populates="account")

    @validates("user_id", "group_id")
    def validate_user_or_group(self, key, value):
        if key == "user_id" and value is not None and self.group_id is not None:
            raise ValueError("Аккаунт не может быть и персональным и групповым.")
        if key == "group_id" and value is not None and self.user_id is not None:
            raise ValueError("Аккаунт не может быть и персональным и групповым.")
        return value
