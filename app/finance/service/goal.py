import logging
from dataclasses import dataclass
from typing import List

from app.finance.exception import GoalNotFound, AccessDeniedGoal, GoalsNotFound
from app.finance.repository import GoalRepository
from app.finance.schema import GoalResponseSchema, GoalCreateSchema, GoalUpdateAmountSchema
from app.groups.models.group_member import RoleEnum
from app.groups.service import GroupMemberService
from app.users.service import AccountService

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class GoalService:
    goal_repository: GoalRepository
    group_member_service: GroupMemberService
    account_service: AccountService

    async def create_goal(self,
                          user_id: int,
                          goal_user_data: GoalCreateSchema,
                          ) -> GoalResponseSchema:

        goal_user = await self.goal_repository.create_goal(goal_data=goal_user_data, user_id=user_id)
        return GoalResponseSchema.model_validate(goal_user)

    async def get_goal_by_account_id(self, account_id: int, user_id: int) -> List[GoalResponseSchema]:
        account = await self.account_service.get_account_by_anything(account_id=account_id)

        if account.user_id:
            goals = await self.goal_repository.get_personal_goals(
                account_id=account_id,
                user_id=user_id)
            if not goals:
                raise GoalsNotFound("Цели не найдены")
            return [GoalResponseSchema.model_validate(goal) for goal in goals]

        if account.group_id:
            goals = await self.goal_repository.get_group_goals(
                group_id=account.group_id)
            if not goals:
                raise GoalsNotFound("Цели не найдены")
            return [GoalResponseSchema.model_validate(goal) for goal in goals]

        else:
            raise GoalsNotFound("Некорректные данные аккаунта")

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
        goal = await self.get_goal_by_id(update_data.goal_update_id)
        account = await self.account_service.get_account_by_anything(account_id=goal.account_id)

        if account.group_id:
            await self.group_member_service.belongs_user_to_group(group_id=account.group_id, user_id=user_id)

        if account.user_id and account.user_id != user_id:
            raise AccessDeniedGoal("Недостаточно прав для обновления этой цели")

        updated_goal = await self.goal_repository.update_goal_amount(
            goal_id=update_data.goal_update_id, contribute_amount=update_data.contribute_amount
        )
        return GoalResponseSchema.model_validate(updated_goal)

    async def delete_goal(self, user_id: int, goal_id: int) -> None:
        goal = await self.get_goal_by_id(goal_id)
        account = await self.account_service.get_account_by_anything(account_id=goal.account_id)

        if account.group_id:
            group_member = await self.group_member_service.belongs_user_to_group(group_id=account.group_id,
                                                                                 user_id=user_id)
            if group_member.role != RoleEnum.ADMIN.value:
                raise AccessDeniedGoal("Только администратор может удалить цель")

        if account.user_id and account.user_id != user_id:
            raise AccessDeniedGoal("Недостаточно прав для обновления этой цели")

        await self.goal_repository.delete_goal(goal_id)
