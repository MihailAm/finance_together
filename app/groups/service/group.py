from dataclasses import dataclass

from app.groups.exception import GroupNotFound, AccessDenied
from app.groups.models.group_member import RoleEnum
from app.groups.repository.group import GroupRepository
from app.groups.schema import GroupSchema
from app.groups.service.group_member import GroupMemberService
from app.settings import Settings


@dataclass
class GroupService:
    setting: Settings
    group_repository: GroupRepository
    group_member_service: GroupMemberService

    async def create_group(self, name: str, user_id: int) -> GroupSchema:
        group = await self.group_repository.create_group(name=name, user_id=user_id)
        return GroupSchema.model_validate(group)

    async def get_group_info(self, group_id: int, user_id: int) -> GroupSchema:
        group = await self.group_repository.get_group_by_id(group_id=group_id)
        if not group:
            raise GroupNotFound(f"Группа с ID {group_id} не найдена")

        await self.group_member_service.belongs_user_to_group(group_id=group_id, user_id=user_id)
        return group

    async def delete_group(self, group_id: int, user_id: int) -> None:
        group = await self.group_repository.get_group_by_id(group_id)
        if not group:
            raise GroupNotFound(f"Группа с ID {group_id} не найдена")

        member = await self.group_member_service.belongs_user_to_group(group_id=group_id, user_id=user_id)
        if not member or member.role != RoleEnum.ADMIN.value:
            raise AccessDenied("Только администратор может удалить группу")

        await self.group_repository.delete_group(group_id=group_id)
