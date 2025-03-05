from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.finance.models.transaction import TransactionType


class TransactionResponseSchema(BaseModel):
    id: int
    amount: float
    description: str | None
    transaction_date: datetime
    type: TransactionType
    account_id: int
    user_id: int
    category_id: int | None

    model_config = ConfigDict(from_attributes=True)


class CreateTransactionSchema(BaseModel):
    amount: float
    description: str | None = None
    type: TransactionType
    account_id: int
    category_id: int | None = None
