from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.finance.models.planned_expenses import PlannedExpenseType


class PlannedExpensesResponseSchema(BaseModel):
    id: int
    amount: float
    description: str | None
    dur_date: datetime
    type: PlannedExpenseType
    account_id: int
    user_id: int
    category_id: int

    model_config = ConfigDict(from_attributes=True)


class PlannedExpensesCreateSchema(BaseModel):
    amount: float
    description: str | None = None
    dur_date: datetime
    type: PlannedExpenseType
    account_id: int
    category_id: int
