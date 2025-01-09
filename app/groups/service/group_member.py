from dataclasses import dataclass
from typing import List

from app.groups.exception import UserNotFoundInGroup, GroupNotFound, AccessDenied
from app.groups.models.group_member import RoleEnum
from app.groups.repository import GroupMemberRepository
from app.groups.schema import GroupMemberSchema, UserGroupResponse, DeleteMemberSchema, AddMemberSchema, \
    ChangeMemberSchema
from app.settings import Settings
from app.users.service import UserService


@dataclass
class GroupMemberService:
    setting: Settings
    group_member_repository: GroupMemberRepository
    user_profile_service: UserService

    async def belongs_user_to_group(self, group_id: int, user_id: int) -> GroupMemberSchema:
        group = await self.group_member_repository.search_user_in_group(group_id=group_id, user_id=user_id)
        if not group:
            raise UserNotFoundInGroup(
                "Данный пользователь, который пытается выполнить данное действие не состоит в этой группе")
        return GroupMemberSchema.model_validate(group)

    async def get_groups_user(self, user_id: int) -> List[UserGroupResponse]:
        groups = await self.group_member_repository.get_groups_user(user_id=user_id)
        if not groups:
            raise GroupNotFound("Данный пользователь не состоит ни в одной группе")
        return groups

    async def add_member(self, member: AddMemberSchema, user_id: int) -> GroupMemberSchema:
        await self.belongs_user_to_group(group_id=member.group_id, user_id=user_id)

        new_member = await self.user_profile_service.get_user_by_email(email=member.email)

        new_members_group = await self.group_member_repository.add_member(group_id=member.group_id,
                                                                          new_member_id=new_member.id,
                                                                          role=member.role)

        return new_members_group

    async def remove_member(self, member: DeleteMemberSchema, user_id: int) -> None:
        user = await self.belongs_user_to_group(group_id=member.group_id, user_id=user_id)
        if not user or user.role != RoleEnum.ADMIN.value:
            raise AccessDenied("Только администратор может выгнать человека")

        await self.group_member_repository.delete_member(group_id=member.group_id, user_id=member.member_id)

    async def change_role(self, body: ChangeMemberSchema, user_id: int) -> GroupMemberSchema:
        user = await self.belongs_user_to_group(group_id=body.group_id, user_id=user_id)
        if not user or user.role != RoleEnum.ADMIN.value:
            raise AccessDenied("Только администратор может изменить роль человека")

        member = await self.group_member_repository.change_role(member=body)
        return GroupMemberSchema.model_validate(member)

    async def get_members_group(self, group_id: int, user_id: int) -> List[GroupMemberSchema]:
        await self.belongs_user_to_group(group_id=group_id, user_id=user_id)

        members_group = await self.group_member_repository.get_members_group(group_id=group_id)
        return [GroupMemberSchema.model_validate(members) for members in members_group]
