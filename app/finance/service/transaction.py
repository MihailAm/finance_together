import logging
from dataclasses import dataclass
from typing import List

from app.finance.exception import TransactionNotFound, AccessDeniedTransaction
from app.finance.models.transaction import TransactionType
from app.finance.repository import TransactionRepository
from app.finance.schema import CreateTransactionSchema, TransactionResponseSchema
from app.groups.exception import AccessDenied
from app.users.service import AccountService

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class TransactionService:
    transaction_repository: TransactionRepository
    account_service: AccountService

    async def create_transaction(self,
                                 transaction_data: CreateTransactionSchema,
                                 user_id: int) -> TransactionResponseSchema:
        account = await self.account_service.get_account_by_anything(account_id=transaction_data.account_id)

        if account.user_id:
            if account.user_id != user_id:
                raise AccessDenied("Нет доступа к этому личному аккаунту")

        transaction = await self.transaction_repository.create_transaction(transaction_data=transaction_data,
                                                                           user_id=user_id)

        if transaction.type.value == "доход":
            await self.account_service.deposit_account(account_id=transaction.account_id,
                                                       amount=transaction.amount,
                                                       user_id=transaction.user_id)

        if transaction.type.value == "расход":
            await self.account_service.withdraw_account(account_id=transaction.account_id,
                                                        amount=transaction.amount,
                                                        user_id=transaction.user_id)

        return TransactionResponseSchema.model_validate(transaction)

    async def get_transactions(self, account_id: int, user_id: int) -> List[TransactionResponseSchema]:

        account = await self.account_service.get_account_by_anything(account_id=account_id)

        if account.user_id:
            transactions = await self.transaction_repository.get_personal_transactions(account_id=account_id,
                                                                                       user_id=user_id)
            if not transactions:
                raise TransactionNotFound("Транзакции не найдены")
            return [TransactionResponseSchema.model_validate(transaction) for transaction in transactions]

        if account.group_id:
            transactions = await self.transaction_repository.get_group_transactions(group_id=account.group_id)
            if not transactions:
                raise TransactionNotFound("Транзакции не найдены")
            return [TransactionResponseSchema.model_validate(transaction) for transaction in transactions]

        else:
            raise TransactionNotFound("Некорректные данные аккаунта")

    async def delete_transaction(self, transaction_id: int, user_id: int) -> None:
        transaction = await self.transaction_repository.get_transaction_by_id(transaction_id=transaction_id)
        if not transaction:
            raise TransactionNotFound("Транзакции не найдены")
        account = await self.account_service.get_account_by_anything(account_id=transaction.account_id)

        if transaction.user_id != user_id:
            raise AccessDeniedTransaction("Доступ к транзакции не доступен")

        if transaction.type == TransactionType.INCOME:
            await self.account_service.withdraw_account(account_id=account.id,
                                                        amount=transaction.amount,
                                                        user_id=user_id)
        elif transaction.type == TransactionType.EXPENSE:
            await self.account_service.deposit_account(account_id=account.id,
                                                       amount=transaction.amount,
                                                       user_id=user_id)

        await self.transaction_repository.delete_transaction(transaction_id=transaction.id)
