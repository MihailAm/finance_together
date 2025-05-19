from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from app.finance.exception import TransactionNotFound, PlannedExpensesNotFound
from app.finance.repository import StatsRepository
from app.finance.schema import StatTransactionSchema, PlannedExpensesResponseSchema, PlannedExpensesStats
from app.users.service import AccountService


@dataclass
class StatsService:
    account_service: AccountService
    stats_repository: StatsRepository

    async def get_stats_transactions(self, account_id: int,
                                     user_id: int,
                                     start_date: Optional[datetime] = None,
                                     end_date: Optional[datetime] = None):
        account = await self.account_service.get_account_by_anything(account_id=account_id)

        if account.user_id:
            transactions = await self.stats_repository.get_personal_transactions(account_id=account_id,
                                                                                 start_date=start_date,
                                                                                 end_date=end_date,
                                                                                 user_id=user_id)
            if not transactions:
                raise TransactionNotFound("Транзакции не найдены")
            return [StatTransactionSchema.model_validate(transaction) for transaction in transactions]

        if account.group_id:
            transactions = await self.stats_repository.get_group_transactions(group_id=account.group_id,
                                                                              start_date=start_date,
                                                                              end_date=end_date, )
            if not transactions:
                raise TransactionNotFound("Транзакции не найдены")
            return [StatTransactionSchema.model_validate(transaction) for transaction in transactions]

        else:
            raise TransactionNotFound("Некорректные данные аккаунта")

    async def get_planned_expenses(self, account_id: int, user_id: int, dur_date: datetime) -> List[
        PlannedExpensesStats]:

        account = await self.account_service.get_account_by_anything(account_id=account_id)

        if account.user_id:
            planned_expenses = await self.stats_repository.get_personal_planned_expenses(
                account_id=account_id,
                user_id=user_id,
                dur_date=dur_date)
            if not planned_expenses:
                raise PlannedExpensesNotFound("Плановых операций не найдено")
            return [PlannedExpensesStats.model_validate(expenses) for expenses in planned_expenses]

        if account.group_id:
            planned_expenses = await self.stats_repository.get_group_planned_expenses(
                group_id=account.group_id, dur_date=dur_date)
            if not planned_expenses:
                raise PlannedExpensesNotFound("Плановых операций не найдено")
            return [PlannedExpensesStats.model_validate(expenses) for expenses in planned_expenses]

        else:
            raise PlannedExpensesNotFound("Некорректные данные аккаунта")
