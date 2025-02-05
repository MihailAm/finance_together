import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select, update

from app.finance.models import GoalContribution, Goal
from app.finance.models.transaction import TransactionType, FinanceTransaction
from app.finance.schema import CreateTransactionSchema

from app.infrastructure.database import get_db_session
from app.users.models import Account

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class CronJobGoal:

    @staticmethod
    async def get_active_goals():

        query = select(GoalContribution).where(GoalContribution.is_active_pay == True)

        async for session in get_db_session():
            goal_contributions = (await session.execute(query)).scalars()
            logger.debug(f"ЭТО ПОИСК АКТИВНЫХ ПЕРЕВОДОВ {goal_contributions}")
            return list(goal_contributions)

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
            logger.debug(f"ЭТО СОЗДАНИЕ ТРАНЗАКЦИИ {transaction}")
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
            logger.debug(f"ЭТО ДЕПОЗИТ АККАУНТА {account}")
            return account

    @staticmethod
    async def get_account_id_by_goal(goal_id: int) -> int:

        query = (
            select(Goal)
            .where(Goal.id == goal_id)
        )

        async for session in get_db_session():
            goal: Goal = (await session.execute(query)).scalar_one_or_none()
            logger.debug(f"ЭТО ДЕПОЗИТ АККАУНТА {goal.account_id}")
            return goal.account_id

    async def process_auto_payments(self):
        goal_contributions = await self.get_active_goals()
        now = datetime.now()
        last_30_days = now - timedelta(days=30)

        contributions = [
            contrib for contrib in goal_contributions if contrib.contributed_at >= last_30_days
        ]
        logger.debug(
            f"ЗДЕСЬ МЫ ОТОБРАЛИ АКТИВНЫЕ ПЕРЕВОДЫ ДО НУЖНОЙ ДАТЫ {[await self.get_account_id_by_goal(i.goal_id) for i in contributions]}")

        for contribution in contributions:
            data = CreateTransactionSchema(
                amount=contribution.amount,
                type=TransactionType.EXPENSE,
                account_id=await self.get_account_id_by_goal(contribution.goal_id))
            logger.debug(f"ЗДЕСЬ МЫ СОЗДАЛИ ОДНУ ТРАНЗАКЦИЮ")
            transaction = await self.create_transaction(transaction_data=data,
                                                        user_id=contribution.user_id)

            deposit = await self.deposit_balance(account_id=transaction.account_id, amount=-transaction.amount)

            print(f"✅ Транзакция: {transaction.id} {transaction.amount} успешно создана")
            print(f"✅ Баланс аккаунта: {deposit.account_name}  равен {deposit.balance}")
