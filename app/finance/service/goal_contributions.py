from dataclasses import dataclass
from typing import List

from app.finance.exception import AccessDeniedGoal, GoalContribForbidden, GoalContribNotFound
from app.finance.repository import GoalContributionsRepository
from app.finance.schema import CreateGoalContributionSchema, GoalUpdateAmountSchema, ResponseGoalContributionSchema
from app.finance.service import GoalService
from app.groups.service import GroupMemberService
from app.users.service import AccountService


@dataclass
class GoalContributionsService:
    goal_service: GoalService
    goal_contribution_repository: GoalContributionsRepository
    account_service: AccountService
    group_member_service: GroupMemberService

    async def create_goal_contributions(self, user_id: int,
                                        goal_contrib_user_data: CreateGoalContributionSchema) -> ResponseGoalContributionSchema:
        new_goal_contrib = await self.goal_contribution_repository.create_goal_contrib(data=goal_contrib_user_data,
                                                                                       user_id=user_id)

        update_data = GoalUpdateAmountSchema(
            goal_update_id=new_goal_contrib.goal_id,
            contribute_amount=new_goal_contrib.amount
        )

        await self.goal_service.update_goal_amount(user_id=new_goal_contrib.user_id,
                                                   update_data=update_data)

        return ResponseGoalContributionSchema.model_validate(new_goal_contrib)

    async def get_goal_contributions_by_user_goal_id(self, goal_id: int, user_id: int) -> List[
        ResponseGoalContributionSchema]:
        goal = await self.goal_service.get_goal_by_id(goal_id=goal_id)
        account = await self.account_service.get_account_by_anything(account_id=goal.account_id)

        if account.group_id:
            await self.group_member_service.belongs_user_to_group(group_id=account.group_id, user_id=user_id)

        if account.user_id and account.user_id != user_id:
            raise AccessDeniedGoal("Недостаточно прав для получения истории пополнений этой цели")

        goal_contributions = await self.goal_contribution_repository.get_goal_contributions(goal_id=goal_id)

        return [ResponseGoalContributionSchema.model_validate(goal_contrib) for goal_contrib in goal_contributions]

    async def get_goal_contrib_by_id(self, goal_contrib_id: int) -> ResponseGoalContributionSchema:
        goal_contrib = await self.goal_contribution_repository.get_goal_contrib_by_id(goal_contrib_id=goal_contrib_id)
        if not goal_contrib:
            raise GoalContribNotFound("Перевод с таким идентификатором не найден")
        return ResponseGoalContributionSchema.model_validate(goal_contrib)

    async def toggle_is_active_pay(self, contribution_id: int,
                                   is_active_pay: bool,
                                   user_id: int) -> ResponseGoalContributionSchema:
        goal_contrib = await self.get_goal_contrib_by_id(goal_contrib_id=contribution_id)
        if goal_contrib.user_id != user_id:
            raise GoalContribForbidden("Вы не можете упралять данной операцией")

        updated_contribution = await self.goal_contribution_repository.update_is_active_pay(goal_contrib_id=contribution_id,
                                                                                      flag=is_active_pay)

        return ResponseGoalContributionSchema.model_validate(updated_contribution)
