from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.finance.models.transaction import TransactionType


class StatTransactionSchema(BaseModel):
    name: str
    surname: str
    account_name: str
    amount: float
    description: str | None
    transaction_date: datetime
    type: TransactionType
    category_name: str

    model_config = ConfigDict(from_attributes=True)
