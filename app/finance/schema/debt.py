from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.finance.models.debt import DebtStatus


class DebtCreateSchema(BaseModel):
    name: str
    amount: float
    description: str | None = None
    due_date: datetime


class DebtResponseSchema(BaseModel):
    id: int
    name: str
    amount: float
    description: str | None
    due_date: datetime
    status: DebtStatus

    user_id: int

    model_config = ConfigDict(from_attributes=True)

class DebtUpdateAmountSchema(BaseModel):
    id: int
    amount: float
