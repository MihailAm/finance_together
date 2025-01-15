from dataclasses import dataclass
from typing import List

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.finance.models import Debt
from app.finance.schema import DebtCreateSchema


@dataclass
class DebtRepository:
    db_session: AsyncSession

    async def create_debt(self, debt_data: DebtCreateSchema, user_id: int) -> Debt:
        debt = Debt(
            name=debt_data.name,
            amount=debt_data.amount,
            description=debt_data.description,
            due_date=debt_data.due_date,
            user_id=user_id
        )


        async with self.db_session as session:
            session.add(debt)
            await session.commit()
            return debt

    async def get_debt_by_user_id(self, user_id: int) -> List[Debt] | None:
        query = select(Debt).where(Debt.user_id == user_id)

        async with self.db_session as session:
            debts = (await session.execute(query)).scalars().all()

            return list(debts)

    async def update_debt_amount(self, debt_id: int, amount: float) -> Debt:
        query = (
            update(Debt)
            .where(Debt.id == debt_id)
            .values(amount=Debt.amount - amount)
            .returning(Debt)
        )

        async with self.db_session as session:
            new_debt = (await session.execute(query)).scalar()
            await session.commit()
            return new_debt

    async def delete_debt(self, debt_id: int) -> None:
        query = delete(Debt).where(Debt.id == debt_id)
        async with self.db_session as session:
            await session.execute(query)
            await session.commit()

    async def get_debt_by_id(self, debt_id: int) -> Debt | None:
        query = select(Debt).where(Debt.id == debt_id)
        async with self.db_session as session:
            result = await session.execute(query)
            return result.scalar_one_or_none()
