from dataclasses import dataclass
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.finance.models import GoalContribution
from app.finance.schema import CreateGoalContributionSchema


@dataclass
class GoalContributionsRepository:
    db_session: AsyncSession

    async def create_goal_contrib(self, data: CreateGoalContributionSchema,
                                  user_id: int) -> GoalContribution:
        goal_contrib = GoalContribution(amount=data.amount,
                                        is_active_pay=data.is_active_pay,
                                        goal_id=data.goal_id,
                                        user_id=user_id)

        async with self.db_session as session:
            session.add(goal_contrib)
            await session.commit()
            return goal_contrib

    async def get_goal_contributions(self, goal_id: int) -> List[GoalContribution]:
        query = select(GoalContribution).where(GoalContribution.goal_id == goal_id)

        async with self.db_session as session:
            goal_contributions = (await session.execute(query)).scalars()
            return list(goal_contributions)
