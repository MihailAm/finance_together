from dataclasses import dataclass
from typing import List

from app.finance.exception import DebtNotFound, AccessDeniedDebt
from app.finance.repository import DebtRepository
from app.finance.schema import DebtResponseSchema, DebtCreateSchema, DebtUpdateAmountSchema


@dataclass
class DebtService:
    debt_repository: DebtRepository

    async def create_debt(self,
                          user_id: int,
                          debt_user_data: DebtCreateSchema,
                          ) -> DebtResponseSchema:

        goal_user = await self.debt_repository.create_debt(debt_data=debt_user_data, user_id=user_id)
        return DebtResponseSchema.model_validate(goal_user)

    async def get_debt_by_user_id(self, user_id: int) -> List[DebtResponseSchema]:
        user_debt = await self.debt_repository.get_debt_by_user_id(user_id=user_id)
        if not user_debt:
            raise DebtNotFound("Не найдено личных долгов")

        return [DebtResponseSchema.model_validate(debt) for debt in user_debt]

    async def get_debt_by_id(self, debt_id: int) -> DebtResponseSchema:
        debt = await self.debt_repository.get_debt_by_id(debt_id=debt_id)
        if not debt:
            raise DebtNotFound("Не найдено личных долгов")

        return DebtResponseSchema.model_validate(debt)

    async def update_debt_amount(self, user_id: int, update_data: DebtUpdateAmountSchema) -> DebtResponseSchema:
        debt = await self.get_debt_by_id(debt_id=update_data.id)

        if debt.user_id != user_id:
            raise AccessDeniedDebt("Недостаточно прав для обновления этого долга")

        updated_debt = await self.debt_repository.update_debt_amount(
            debt_id=update_data.id, amount=update_data.amount
        )
        return DebtResponseSchema.model_validate(updated_debt)

    async def delete_debt(self, user_id: int, debt_id: int) -> None:
        debt = await self.get_debt_by_id(debt_id=debt_id)

        if debt.user_id != user_id:
            raise AccessDeniedDebt("Недостаточно прав для обновления этой цели")

        await self.debt_repository.delete_debt(debt_id=debt_id)
