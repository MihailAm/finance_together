from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError

from app.groups.service.group_member import GroupMemberService
from app.settings import Settings
from app.users.exception import AccountNotFound, GroupAccountConflictException, AccountAccessError
from app.users.repository import AccountRepository
from app.users.schema import AccountSchema, AccountCreateSchemaUser


@dataclass
class AccountService:
    setting: Settings
    account_repository: AccountRepository
    group_member_service: GroupMemberService

    async def all_accounts(self, user_id) -> list[AccountSchema]:
        accounts = await self.account_repository.get_accounts(user_id)
        if not accounts:
            raise AccountNotFound("У пользователя не найдено ни одного аккаунта")

        account_schema = [AccountSchema.model_validate(account) for account in accounts]
        return account_schema

    async def create_user_account(self, body: AccountCreateSchemaUser, user_id: int) -> AccountSchema:
        account_id = await self.account_repository.create_account(account=body, user_id=user_id)
        account = await self.account_repository.get_account(account_id=account_id, user_id=user_id)
        return AccountSchema.model_validate(account)

    async def create_group_account(self, name: str, group_id: int) -> AccountSchema:
        try:
            account_group_id = await self.account_repository.create_account_group(account_name=name, group_id=group_id)
            account = await self.account_repository.get_account(group_id=account_group_id)

            return AccountSchema.model_validate(account)

        except IntegrityError:
            raise GroupAccountConflictException("У группы может быть только один аккаунт")

    async def get_group_account(self, group_id: int, user_id: int) -> AccountSchema:
        account = await self.account_repository.get_account(group_id=group_id)
        if not account:
            raise AccountNotFound("У группы нет аккаунта")

        if await self.group_member_service.belongs_user_to_group(group_id=group_id, user_id=user_id):
            return AccountSchema.model_validate(account)

    async def update_account_name(self, account_id: int, account_name: str, user_id: int) -> AccountSchema:
        account = await self.account_repository.get_account(user_id=user_id, account_id=account_id)
        if not account:
            raise AccountNotFound("Аккаунт не найден")
        account = await self.account_repository.update_account_name(account_id=account_id, account_name=account_name)
        return AccountSchema.model_validate(account)

    async def deposit_account(self, account_id: int, amount: float, user_id: int) -> AccountSchema:
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")

        account = await self.account_repository.get_account(account_id)

        if not account:
            raise AccountNotFound("Аккаунт не существует или не является ни личным, ни групповым")

        if account.user_id is not None:
            if account.user_id != user_id:
                raise AccountAccessError("У вас нет доступа к этому личному аккаунту")
            account_update = await self.account_repository.deposit_balance(account.id, amount)
            return AccountSchema.model_validate(account_update)

        if account.group_id is not None:
            if not await self.group_member_service.belongs_user_to_group(group_id=account.group_id, user_id=user_id):
                raise AccountAccessError("Вы не состоите в этой группе")
            account_update = await self.account_repository.deposit_balance(account.id, amount)
            return AccountSchema.model_validate(account_update)

    async def withdraw_account(self, account_id: int, amount: float, user_id: int) -> AccountSchema:
        if amount <= 0:
            raise ValueError("Сумма для снятия должна быть положительной")

        account = await self.account_repository.get_account(account_id)

        if not account:
            raise AccountNotFound("Аккаунт не существует или не является ни личным, ни групповым")

        if account.user_id is not None:
            if account.user_id != user_id:
                raise AccountAccessError("У вас нет доступа к этому личному аккаунту")
            account_update = await self.account_repository.deposit_balance(account.id, -amount)
            return AccountSchema.model_validate(account_update)

        elif account.group_id is not None:
            if not await self.group_member_service.belongs_user_to_group(group_id=account.group_id, user_id=user_id):
                raise AccountAccessError("Вы не состоите в этой группе")
            account_update = await self.account_repository.deposit_balance(account.id, -amount)
            return AccountSchema.model_validate(account_update)
