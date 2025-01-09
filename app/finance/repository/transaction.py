from dataclasses import dataclass
from typing import List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.finance.models import FinanceTransaction
from app.finance.schema import CreateTransactionSchema


@dataclass
class TransactionRepository:
    db_session: AsyncSession

    async def get_personal_transactions(self, account_id: int, user_id: int) -> List[FinanceTransaction] | None:
        query = (
            select(FinanceTransaction)
            .where(FinanceTransaction.account_id == account_id,
                   FinanceTransaction.account.has(user_id=user_id),
                   FinanceTransaction.user_id == user_id)
            .order_by(FinanceTransaction.transaction_date.desc())
        )
        async with self.db_session as session:
            result_transactions = (await session.execute(query)).scalars().all()

        return list(result_transactions)

    async def get_group_transactions(self, group_id: int) -> List[FinanceTransaction] | None:
        query = (
            select(FinanceTransaction)
            .where(FinanceTransaction.account.has(group_id=group_id))
            .order_by(FinanceTransaction.transaction_date.desc())

        )
        async with self.db_session as session:
            result_transactions = (await session.execute(query)).scalars().all()

        return list(result_transactions)

    async def create_transaction(self, transaction_data: CreateTransactionSchema, user_id: int) -> FinanceTransaction:
        transaction = FinanceTransaction(
            amount=transaction_data.amount,
            description=transaction_data.description,
            type=transaction_data.type,
            account_id=transaction_data.account_id,
            user_id=user_id,
            category_id=transaction_data.category_id
        )

        async with self.db_session as session:
            session.add(transaction)
            await session.commit()
            return transaction

    async def get_transaction_by_id(self, transaction_id: int) -> FinanceTransaction | None:
        query = select(FinanceTransaction).where(FinanceTransaction.id == transaction_id)

        async with self.db_session as session:
            transaction = (await session.execute(query)).scalar_one_or_none()

        return transaction

    async def delete_transaction(self, transaction_id: int) -> None:
        query = delete(FinanceTransaction).where(FinanceTransaction.id == transaction_id)

        async with self.db_session as session:
            await session.execute(query)
            await session.commit()
