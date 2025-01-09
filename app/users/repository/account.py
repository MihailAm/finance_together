from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import Account
from app.users.schema import AccountCreateSchemaUser


@dataclass
class AccountRepository:
    db_session: AsyncSession

    async def get_accounts(self, user_id) -> list[Account] | None:
        query = select(Account).where(Account.user_id == user_id)

        async with self.db_session as session:
            result = await session.execute(query)
            account: list[Account] = list(result.scalars().all())

        return account

    async def create_account(self, account: AccountCreateSchemaUser, user_id: int) -> int:
        account_model = Account(account_name=account.account_name,
                                user_id=user_id
                                )

        async with self.db_session as session:
            session.add(account_model)
            await session.commit()
            return account_model.id

    async def get_account(self,
                          account_id: Optional[int] = None,
                          user_id: Optional[int] = None,
                          group_id: Optional[int] = None) -> Account | None:
        query = select(Account)

        if account_id:
            query = query.where(Account.id == account_id)
        if user_id:
            query = query.where(Account.user_id == user_id)
        if group_id:
            query = query.where(Account.group_id == group_id)

        async with self.db_session as session:
            account = (await session.execute(query)).scalar_one_or_none()

        return account

    async def create_account_group(self, account_name: str, group_id: int) -> int:
        account_model = Account(account_name=account_name,
                                group_id=group_id
                                )

        async with self.db_session as session:
            session.add(account_model)
            await session.commit()
            return account_model.group_id

    async def update_account_name(self, account_id: int, account_name: str) -> Account:
        query = update(Account).where(Account.id == account_id).values(account_name=account_name).returning(Account)

        async with self.db_session as session:
            account: Account = (await session.execute(query)).scalar_one_or_none()
            await session.commit()
            return account

    async def deposit_balance(self, account_id: int, amount: float) -> Account:
        query = (
            update(Account)
            .where(Account.id == account_id)
            .values(balance=Account.balance + amount)
            .returning(Account)
        )

        async with self.db_session as session:
            account: Account = (await session.execute(query)).scalar_one_or_none()
            await session.commit()
            return account
