from dataclasses import dataclass
from typing import List

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.finance.models import Goal
from app.finance.schema import GoalCreateSchema


@dataclass
class GoalRepository:
    db_session: AsyncSession

    async def create_goal(self, goal_data: GoalCreateSchema,
                          user_id: int | None = None) -> Goal:
        goal = Goal(
            name=goal_data.name,
            target_amount=goal_data.target_amount,
            current_amount=goal_data.current_amount,
            description=goal_data.description,
            due_date=goal_data.due_date,
            status=goal_data.status,
            user_id=user_id,
            account_id=goal_data.account_id
        )

        async with self.db_session as session:
            session.add(goal)
            await session.commit()
            return goal

    async def get_personal_goals(self, account_id: int, user_id: int) -> List[Goal] | None:
        query = (
            select(Goal)
            .where(Goal.account_id == account_id,
                   Goal.account.has(user_id=user_id),
                   Goal.user_id == user_id)
            .order_by(Goal.due_date.desc())
        )
        async with self.db_session as session:
            result_goals = (await session.execute(query)).scalars().all()

        return list(result_goals)

    async def get_group_goals(self, group_id: int) -> List[Goal] | None:
        query = (
            select(Goal)
            .where(Goal.account.has(group_id=group_id))
            .order_by(Goal.dur_date.desc())

        )
        async with self.db_session as session:
            result_goals = (await session.execute(query)).scalars().all()

        return list(result_goals)

    async def get_goal_by_user_id(self, user_id: int) -> List[Goal] | None:
        query = select(Goal).where(Goal.user_id == user_id)

        async with self.db_session as session:
            goals = (await session.execute(query)).scalars().all()

            return list(goals)

    async def update_goal_amount(self, goal_id: int, contribute_amount: float) -> Goal:
        query = (
            update(Goal)
            .where(Goal.id == goal_id)
            .values(current_amount=Goal.current_amount + contribute_amount)
            .returning(Goal)
        )

        async with self.db_session as session:
            new_goal = (await session.execute(query)).scalar()
            await session.commit()
            return new_goal

    async def delete_goal(self, goal_id: int) -> None:
        query = delete(Goal).where(Goal.id == goal_id)
        async with self.db_session as session:
            await session.execute(query)
            await session.commit()

    async def get_goal_by_id(self, goal_id: int) -> Goal | None:
        query = select(Goal).where(Goal.id == goal_id)
        async with self.db_session as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()
