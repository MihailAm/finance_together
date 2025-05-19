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


from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PlannedExpensesStats(BaseModel):
    id: int
    name: str
    amount: float
    description: Optional[str] = None
    dur_date: datetime
    type: str
    user_name: str
    user_surname: str
    category_name: Optional[str] = None
    account_name: str
    # is_active_pay: bool
    # user_id: int
    # category_id: int
