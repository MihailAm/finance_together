from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CreateGoalContributionSchema(BaseModel):
    amount: float
    is_active_pay: bool = False
    goal_id: int


class ResponseGoalContributionSchema(BaseModel):
    id: int
    amount: float
    contributed_at: datetime
    is_active_pay: bool

    goal_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
