import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select, update

from app.finance.models import GoalContribution, Goal, PlannedExpenses
from app.finance.models.transaction import TransactionType, FinanceTransaction
from app.finance.schema import CreateTransactionSchema

from app.infrastructure.database import get_db_session
from app.users.models import Account

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class CronJobPlannedExpenses:

    @staticmethod
    async def get_active_planned_expenses():
        now = datetime.now().date()
        tomorrow = now + timedelta(days=1)

        query = select(PlannedExpenses).where(PlannedExpenses.is_active_pay == True,
                                              PlannedExpenses.dur_date >= now,
                                              PlannedExpenses.dur_date < tomorrow)

        async for session in get_db_session():
            planned_expenses = (await session.execute(query)).scalars()
            return list(planned_expenses)

    @staticmethod
    async def create_transaction(transaction_data: CreateTransactionSchema,
                                 user_id: int):

        transaction = FinanceTransaction(
            amount=transaction_data.amount,
            description=transaction_data.description,
            type=transaction_data.type,
            account_id=transaction_data.account_id,
            user_id=user_id,
            category_id=transaction_data.category_id
        )

        async for session in get_db_session():
            session.add(transaction)
            await session.commit()
            return transaction

    @staticmethod
    async def deposit_balance(account_id: int, amount: float) -> Account:

        query = (
            update(Account)
            .where(Account.id == account_id)
            .values(balance=Account.balance + amount)
            .returning(Account)
        )

        async for session in get_db_session():
            account: Account = (await session.execute(query)).scalar_one_or_none()
            await session.commit()
            return account

    @staticmethod
    async def get_account_id_by_planned_expenses(planned_consumption_id: int) -> int:

        query = (
            select(PlannedExpenses)
            .where(PlannedExpenses.id == planned_consumption_id)
        )

        async for session in get_db_session():
            planned_consumption: PlannedExpenses = (await session.execute(query)).scalar_one_or_none()

            return planned_consumption.account_id

    async def process_auto_payments(self):
        planned_contributions = await self.get_active_planned_expenses()

        contributions = [contrib for contrib in planned_contributions]

        for contribution in contributions:
            data = CreateTransactionSchema(
                amount=contribution.amount,
                type=TransactionType.EXPENSE,
                account_id=await self.get_account_id_by_planned_expenses(contribution.id))

            transaction = await self.create_transaction(transaction_data=data,
                                                        user_id=contribution.user_id)

            deposit = await self.deposit_balance(account_id=transaction.account_id, amount=-transaction.amount)

            print(f"✅ Транзакция для планового расхода: {transaction.id} {transaction.amount} успешно создана")
            print(f"✅ Баланс аккаунта при плановом расходе: {deposit.account_name}  равен {deposit.balance}")
