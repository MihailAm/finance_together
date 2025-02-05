from dataclasses import dataclass
from typing import List

from sqlalchemy import select, update
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

    async def get_active_goals(self) -> List[GoalContribution]:
        query = select(GoalContribution).where(GoalContribution.is_active_pay == True)

        async with self.db_session as session:
            goal_contributions = (await session.execute(query)).scalars()
            return list(goal_contributions)

    async def get_goal_contrib_by_id(self, goal_contrib_id: int) -> GoalContribution:
        query = select(GoalContribution).where(GoalContribution.id == goal_contrib_id)

        async with self.db_session as session:
            goal_contrib = (await session.execute(query)).scalar()
            return goal_contrib

    async def update_is_active_pay(self, goal_contrib_id: int, flag: bool) -> GoalContribution:
        query = (
            update(GoalContribution).
            where(GoalContribution.id == goal_contrib_id).
            values(is_active_pay=flag).
            returning(GoalContribution)
        )

        async with self.db_session as session:
            new_goal_contrib = (await session.execute(query)).scalar()
            await session.commit()
            return new_goal_contrib
