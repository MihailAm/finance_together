from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.finance.models import FinanceTransaction, Category
from app.finance.schema import StatTransactionSchema
from app.users.models import Account


@dataclass
class StatsRepository:
    db_session: AsyncSession

    async def get_personal_transactions(self,
                                        account_id: int,
                                        user_id: int,
                                        start_date: Optional[datetime] = None,
                                        end_date: Optional[datetime] = None
                                        ) -> List[StatTransactionSchema] | None:
        query = (
            select(FinanceTransaction, Category.name.label("category_name"))
            .join(Category, FinanceTransaction.category_id == Category.id, isouter=True)
            .options(
                joinedload(FinanceTransaction.user),
                joinedload(FinanceTransaction.account)
            )
            .where(
                FinanceTransaction.account_id == account_id,
                FinanceTransaction.user_id == user_id
            )
            .order_by(FinanceTransaction.transaction_date.desc())
        )

        if start_date:
            query = query.where(FinanceTransaction.transaction_date >= start_date)
        if end_date:
            query = query.where(FinanceTransaction.transaction_date <= end_date)

        async with self.db_session as session:
            result = await session.execute(query)
            transactions = []

            for transaction, category_name in result:
                transactions.append(StatTransactionSchema(
                    name=transaction.user.name,
                    surname=transaction.user.surname,
                    account_name=transaction.account.account_name,
                    amount=transaction.amount,
                    description=transaction.description,
                    transaction_date=transaction.transaction_date,
                    type=transaction.type,
                    category_name=category_name if category_name else "Без категории"
                ))

            return transactions if transactions else None


    async def get_group_transactions(self,
                                 group_id: int,
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None
                                 ) -> List[StatTransactionSchema] | None:
        query = (
            select(
                FinanceTransaction,
                Category.name.label("category_name")
            )
            .join(
                Category,
                FinanceTransaction.category_id == Category.id,
                isouter=True
            )

            .join(Account, FinanceTransaction.account_id == Account.id)
            .where(Account.group_id == group_id)
            .options(
                joinedload(FinanceTransaction.user),
            joinedload(FinanceTransaction.account)
            )
            .order_by(FinanceTransaction.transaction_date.desc())
        )

        if start_date:
            query = query.where(FinanceTransaction.transaction_date >= start_date)
        if end_date:
            query = query.where(FinanceTransaction.transaction_date <= end_date)

        async with self.db_session as session:
            result = await session.execute(query)

            transactions = result.unique().all()

            return [
                StatTransactionSchema(
                    name=transaction.user.name,
                    surname=transaction.user.surname,
                    account_name=transaction.account.account_name,
                    amount=transaction.amount,
                    description=transaction.description,
                    transaction_date=transaction.transaction_date,
                    type=transaction.type,
                    category_name=category_name or "Без категории"
                )
                for transaction, category_name in transactions
            ] or None
