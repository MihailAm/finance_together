from datetime import datetime
from enum import Enum

from sqlalchemy import Enum as SQLEnum, DateTime
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base
from app.groups.models.group import Group
from app.users.models.user import UserProfile


class RoleEnum(Enum):
    ADMIN = "Администратор"
    MEMBER = "Участник"


class GroupMember(Base):
    __tablename__ = "group_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_profile.id"))
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("groups.id",ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(SQLEnum(RoleEnum), default=RoleEnum.MEMBER, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    groups = relationship("Group", back_populates="group_members")
