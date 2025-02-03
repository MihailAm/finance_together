from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.finance.models.goal import GoalStatus


class GoalResponseSchema(BaseModel):
    id: int
    name: str
    target_amount: float
    current_amount: float
    description: str
    due_date: datetime
    created_at: datetime
    status: GoalStatus

    user_id: int
    account_id: int

    model_config = ConfigDict(from_attributes=True)


class GoalCreateSchema(BaseModel):
    name: str
    target_amount: float
    current_amount: float
    description: str
    due_date: datetime
    status: GoalStatus = GoalStatus.ACTIVE

    account_id: int


class GoalUpdateAmountSchema(BaseModel):
    goal_update_id: int
    contribute_amount: float
