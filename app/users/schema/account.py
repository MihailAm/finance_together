from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AccountSchema(BaseModel):
    id: int
    account_name: str
    balance: float
    user_id: int | None
    group_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AccountCreateSchemaUser(BaseModel):
    account_name: str


class DepositRequest(BaseModel):
    account_id: int
    amount: float
