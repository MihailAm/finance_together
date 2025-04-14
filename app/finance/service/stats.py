from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.finance.exception import TransactionNotFound
from app.finance.repository import StatsRepository
from app.finance.schema import StatTransactionSchema
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
