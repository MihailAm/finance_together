import logging
from dataclasses import dataclass
from typing import Optional, List

from app.finance.exception import GoalNotFound, AccessDeniedGoal
from app.finance.repository import GoalRepository
from app.finance.schema import GoalResponseSchema, GoalUserCreateSchema, GoalGroupCreateSchema, GoalUpdateAmountSchema
from app.groups.models.group_member import RoleEnum
from app.groups.service import GroupMemberService

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class GoalService:
    goal_repository: GoalRepository
    group_member_service: GroupMemberService

    async def create_goal(self,
                          user_id: int,
                          goal_user_data: Optional[GoalUserCreateSchema] = None,
                          goal_group_data: Optional[GoalGroupCreateSchema] = None) -> GoalResponseSchema:
        if goal_user_data:
            goal_user = await self.goal_repository.create_goal(goal_data=goal_user_data, user_id=user_id)
            return GoalResponseSchema.model_validate(goal_user)

        if goal_group_data:
            await self.group_member_service.belongs_user_to_group(group_id=goal_group_data.group_id, user_id=user_id)
            goal_group = await self.goal_repository.create_goal(goal_data=goal_group_data)
            return GoalResponseSchema.model_validate(goal_group)

    async def get_goal_by_group_id(self, group_id: int, user_id: int) -> List[GoalResponseSchema]:
        await self.group_member_service.belongs_user_to_group(group_id=group_id, user_id=user_id)
        groups_goal = await self.goal_repository.get_goal_by_group_id(group_id=group_id)
        if not groups_goal:
            raise GoalNotFound("Не найдено групповых целей")

        return [GoalResponseSchema.model_validate(goal) for goal in groups_goal]

    async def get_goal_by_user_id(self, user_id: int) -> List[GoalResponseSchema]:
        user_goal = await self.goal_repository.get_goal_by_user_id(user_id=user_id)
        if not user_goal:
            raise GoalNotFound("Не найдено личных целей")

        return [GoalResponseSchema.model_validate(goal) for goal in user_goal]

    async def get_goal_by_id(self, goal_id: int) -> GoalResponseSchema:
        goal = await self.goal_repository.get_goal_by_id(goal_id=goal_id)
        if not goal:
            raise GoalNotFound("Цель не найдена")

        return GoalResponseSchema.model_validate(goal)

    async def update_goal_amount(self, user_id: int, update_data: GoalUpdateAmountSchema) -> GoalResponseSchema:
        goal = await self.get_goal_by_id(update_data.id)

        if goal.group_id:
            await self.group_member_service.belongs_user_to_group(group_id=goal.group_id, user_id=user_id)

        if goal.user_id and goal.user_id != user_id:
            raise AccessDeniedGoal("Недостаточно прав для обновления этой цели")

        updated_goal = await self.goal_repository.update_goal_amount(
            goal_id=update_data.id, target_amount=update_data.target_amount
        )
        return GoalResponseSchema.model_validate(updated_goal)

    async def delete_goal(self, user_id: int, goal_id: int) -> None:
        goal = await self.get_goal_by_id(goal_id)

        if goal.group_id:
            group_member = await self.group_member_service.belongs_user_to_group(group_id=goal.group_id,
                                                                                 user_id=user_id)
            if group_member.role != RoleEnum.ADMIN.value:
                raise AccessDeniedGoal("Только администратор может удалить цель")

        if goal.user_id and goal.user_id != user_id:
            raise AccessDeniedGoal("Недостаточно прав для обновления этой цели")

        await self.goal_repository.delete_goal(goal_id)
