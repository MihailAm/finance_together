from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.finance.models import FinanceTransaction, Category, PlannedExpenses
from app.finance.schema import StatTransactionSchema
from app.users.models import Account, UserProfile


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

    async def get_personal_planned_expenses(self, account_id: int, user_id: int, dur_date: datetime) -> List[
                                                                                                            dict] | None:
        query = (
            select(
                PlannedExpenses.id,
                PlannedExpenses.name,
                PlannedExpenses.amount,
                PlannedExpenses.description,
                PlannedExpenses.dur_date,
                PlannedExpenses.type,
                PlannedExpenses.is_active_pay,
                Account.account_name.label("account_name"),
                UserProfile.name.label("user_name"),
                UserProfile.surname.label("user_surname"),
                Category.name.label("category_name")
            )
            .join(UserProfile, PlannedExpenses.user_id == UserProfile.id)
            .join(Account, PlannedExpenses.account_id == Account.id)
            .join(Category, PlannedExpenses.category_id == Category.id, isouter=True)
            .where(PlannedExpenses.account_id == account_id,
                   PlannedExpenses.account.has(user_id=user_id),
                   PlannedExpenses.user_id == user_id)
            .order_by(PlannedExpenses.dur_date.desc())
        )

        if dur_date:
            query = query.where(PlannedExpenses.dur_date >= dur_date)

        async with self.db_session as session:
            result = await session.execute(query)
            result_planned_expenses = result.mappings().all()

        return [dict(row) for row in result_planned_expenses]

    async def get_group_planned_expenses(self, group_id: int, dur_date: datetime) -> List[dict] | None:
        query = (
            select(
                PlannedExpenses.id,
                PlannedExpenses.name,
                PlannedExpenses.amount,
                PlannedExpenses.description,
                PlannedExpenses.dur_date,
                PlannedExpenses.type,
                PlannedExpenses.is_active_pay,
                UserProfile.name.label("user_name"),
                UserProfile.surname.label("user_surname"),
                Category.name.label("category_name"),
                Account.account_name.label("account_name")
            )
            .join(UserProfile, PlannedExpenses.user_id == UserProfile.id)
            .join(Category, PlannedExpenses.category_id == Category.id, isouter=True)
            .join(Account, PlannedExpenses.account_id == Account.id)
            .where(PlannedExpenses.account.has(group_id=group_id))
            .order_by(PlannedExpenses.dur_date.desc())
        )

        if dur_date:
            query = query.where(PlannedExpenses.dur_date >= dur_date)

        async with self.db_session as session:
            result = await session.execute(query)
            result_planned_expenses = result.mappings().all()

        return [dict(row) for row in result_planned_expenses]
