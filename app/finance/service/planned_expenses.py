from dataclasses import dataclass
from typing import List

from app.finance.exception import PlannedExpensesNotFound
from app.finance.repository import PlannedExpensesRepository
from app.finance.schema import PlannedExpensesCreateSchema, PlannedExpensesResponseSchema
from app.groups.exception import AccessDenied
from app.groups.service import GroupMemberService
from app.users.service import AccountService


@dataclass
class PlannedExpensesService:
    planned_expenses_repository: PlannedExpensesRepository
    group_member_service: GroupMemberService
    account_service: AccountService

    async def create_planned_expenses(self, planned_expenses_data: PlannedExpensesCreateSchema,
                                      user_id: int) -> PlannedExpensesResponseSchema:

        account = await self.account_service.get_account_by_anything(account_id=planned_expenses_data.account_id)
        if account.group_id:
            await self.group_member_service.belongs_user_to_group(group_id=account.group_id, user_id=user_id)

        if account.user_id:
            if account.user_id != user_id:
                raise AccessDenied("Нет доступа к этому личному аккаунту")

        planned_expenses = await self.planned_expenses_repository.create_planned_expenses(
            planned_expenses_data=planned_expenses_data,
            user_id=user_id
        )

        return PlannedExpensesResponseSchema.model_validate(planned_expenses)

    async def get_planned_expenses(self, account_id: int, user_id: int) -> List[PlannedExpensesResponseSchema]:

        account = await self.account_service.get_account_by_anything(account_id=account_id)

        if account.user_id:
            planned_expenses = await self.planned_expenses_repository.get_personal_planned_expenses(
                account_id=account_id,
                user_id=user_id)
            if not planned_expenses:
                raise PlannedExpensesNotFound("Плановых операций не найдено")
            return [PlannedExpensesResponseSchema.model_validate(expenses) for expenses in planned_expenses]

        if account.group_id:
            planned_expenses = await self.planned_expenses_repository.get_group_planned_expenses(
                group_id=account.group_id)
            if not planned_expenses:
                raise PlannedExpensesNotFound("Плановых операций не найдено")
            return [PlannedExpensesResponseSchema.model_validate(expenses) for expenses in planned_expenses]

        else:
            raise PlannedExpensesNotFound("Некорректные данные аккаунта")

    async def delete_planned_expenses(self, planned_expenses_id: int, user_id: int) -> None:
        planned_expenses = await self.planned_expenses_repository.get_planned_expenses_by_id(
            planned_expenses_id=planned_expenses_id
        )
        if not planned_expenses:
            raise PlannedExpensesNotFound("Плановая операция не доступна")
        await self.account_service.get_account_by_anything(account_id=planned_expenses.account_id)

        if planned_expenses.user_id != user_id:
            raise AccessDenied("Доступ к плановой операции не доступен")

        await self.planned_expenses_repository.delete_planned_expenses(planned_expenses_id=planned_expenses.id)
