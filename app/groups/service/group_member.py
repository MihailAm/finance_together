from dataclasses import dataclass

from app.groups.exception import UserNotFoundInGroup
from app.groups.repository import GroupMemberRepository
from app.settings import Settings


@dataclass
class GroupMemberService:
    setting: Settings
    group_member_repository: GroupMemberRepository

    async def belongs_user_to_group(self, group_id: int, user_id: int) -> bool:
        group = await self.group_member_repository.search_user_in_group(group_id=group_id, user_id=user_id)
        if not group:
            raise UserNotFoundInGroup("Данный пользователь не состоит в этой группе")
        return True
