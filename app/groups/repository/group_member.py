import logging
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.groups.models import GroupMember

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class GroupMemberRepository:
    db_session: AsyncSession

    async def search_user_in_group(self, group_id: int, user_id: int) -> GroupMember | None:
        query = select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == user_id)

        async with self.db_session as session:
            member = (await session.execute(query)).scalar_one_or_none()

        return member
