import logging
from dataclasses import dataclass
from typing import List

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.groups.models import GroupMember, Group
from app.groups.models.group_member import RoleEnum
from app.groups.schema import UserGroupResponse, ChangeMemberSchema

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class GroupMemberRepository:
    db_session: AsyncSession

    async def search_user_in_group(self, group_id: int, user_id: int) -> GroupMember | None:
        query = (select(GroupMember)
                 .where(GroupMember.group_id == group_id, GroupMember.user_id == user_id))

        async with self.db_session as session:
            member = (await session.execute(query)).scalar_one_or_none()

        return member

    async def delete_member(self, group_id: int, user_id: int) -> None:
        delete_members_query = (delete(GroupMember)
                                .where(GroupMember.group_id == group_id, GroupMember.user_id == user_id))

        async with self.db_session as session:
            await session.execute(delete_members_query)
            await session.commit()

    async def get_groups_user(self, user_id: int) -> List[UserGroupResponse] | None:
        query = (
            select(
                GroupMember.id,
                GroupMember.user_id,
                Group.name.label("group_name"),
                GroupMember.role.label("role"),
                GroupMember.joined_at
            )
            .join(Group, GroupMember.group_id == Group.id)
            .where(GroupMember.user_id == user_id)
        )

        async with self.db_session as session:
            groups_result = (await session.execute(query)).all()

        return [UserGroupResponse.model_validate(group) for group in groups_result]

    async def add_member(self, group_id: int, new_member_id: int, role: RoleEnum) -> GroupMember:
        group_member = GroupMember(user_id=new_member_id,
                                   group_id=group_id,
                                   role=role)
        async with self.db_session as session:
            session.add(group_member)
            await session.commit()

            return group_member

    async def change_role(self, member: ChangeMemberSchema) -> GroupMember:
        query = (
            update(GroupMember)
            .where(GroupMember.user_id == member.user_id, GroupMember.group_id == member.group_id)
            .values(role=member.role)
            .returning(GroupMember)
        )

        async with self.db_session as session:
            group_member = (await session.execute(query)).scalar()
            await session.commit()

            return group_member

    async def get_members_group(self, group_id: int) -> List[GroupMember]:
        query = select(GroupMember).where(GroupMember.group_id == group_id)

        async with self.db_session as session:
            members_group = (await session.execute(query)).scalars().all()

        return list(members_group)
