from dataclasses import dataclass
from typing import List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.finance.models import PlannedExpenses
from app.finance.schema import PlannedExpensesCreateSchema


@dataclass
class PlannedExpensesRepository:
    db_session: AsyncSession

    async def create_planned_expenses(self,
                                      planned_expenses_data: PlannedExpensesCreateSchema,
                                      user_id: int | None) -> PlannedExpenses:
        planned_expenses = PlannedExpenses(
            name=planned_expenses_data.name,
            amount=planned_expenses_data.amount,
            description=planned_expenses_data.description,
            dur_date=planned_expenses_data.dur_date,
            type=planned_expenses_data.type,
            account_id=planned_expenses_data.account_id,
            user_id=user_id,
            category_id=planned_expenses_data.category_id
        )

        async with self.db_session as session:
            session.add(planned_expenses)
            await session.commit()

        return planned_expenses

    async def get_personal_planned_expenses(self, account_id: int, user_id: int) -> List[PlannedExpenses] | None:
        query = (
            select(PlannedExpenses)
            .where(PlannedExpenses.account_id == account_id,
                   PlannedExpenses.account.has(user_id=user_id),
                   PlannedExpenses.user_id == user_id)
            .order_by(PlannedExpenses.dur_date.desc())
        )
        async with self.db_session as session:
            result_planned_expenses = (await session.execute(query)).scalars().all()

        return list(result_planned_expenses)

    async def get_group_planned_expenses(self, group_id: int) -> List[PlannedExpenses] | None:
        query = (
            select(PlannedExpenses)
            .where(PlannedExpenses.account.has(group_id=group_id))
            .order_by(PlannedExpenses.dur_date.desc())

        )
        async with self.db_session as session:
            result_planned_expenses = (await session.execute(query)).scalars().all()

        return list(result_planned_expenses)

    async def get_planned_expenses_by_id(self, planned_expenses_id: int) -> PlannedExpenses | None:
        query = select(PlannedExpenses).where(PlannedExpenses.id == planned_expenses_id)

        async with self.db_session as session:
            planned_expenses = (await session.execute(query)).scalar_one_or_none()

        return planned_expenses

    async def delete_planned_expenses(self, planned_expenses_id: int) -> None:
        query = delete(PlannedExpenses).where(PlannedExpenses.id == planned_expenses_id)

        async with self.db_session as session:
            await session.execute(query)
            await session.commit()
