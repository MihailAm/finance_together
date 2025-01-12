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

    user_id: int | None
    group_id: int | None

    model_config = ConfigDict(from_attributes=True)


class GoalUserCreateSchema(BaseModel):
    name: str
    target_amount: float
    current_amount: float
    description: str
    due_date: datetime
    status: GoalStatus = GoalStatus.ACTIVE


class GoalGroupCreateSchema(GoalUserCreateSchema):
    group_id: int


class GoalUpdateAmountSchema(BaseModel):
    id: int
    target_amount: float
