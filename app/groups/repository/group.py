import logging
from dataclasses import dataclass

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.groups.models import Group, GroupMember
from app.groups.models.group_member import RoleEnum

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class GroupRepository:
    db_session: AsyncSession

    async def create_group(self, name: str, user_id: int) -> Group:
        async with self.db_session as session:


            new_group = Group(name=name)
            session.add(new_group)
            await session.commit()

            logger.debug(f"айди группы {new_group.id}")
            admin_member = GroupMember(user_id=user_id, group_id=new_group.id, role=RoleEnum.ADMIN)
            session.add(admin_member)

            await session.commit()

        return new_group

    async def get_group_by_id(self, group_id: int) -> Group | None:
        query = select(Group).where(Group.id == group_id)

        async with self.db_session as session:
            group = (await session.execute(query)).scalar_one_or_none()
        return group

    async def delete_group(self, group_id: int) -> None:
        delete_group_query = delete(Group).where(Group.id == group_id)

        async with self.db_session as session:
            await session.execute(delete_group_query)
            await session.commit()
