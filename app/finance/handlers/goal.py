import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends, status, HTTPException

from app.dependecy import get_request_user_id, get_goal_service
from app.finance.exception import GoalNotFound, AccessDeniedGoal
from app.finance.schema import GoalResponseSchema, GoalCreateSchema, GoalUpdateAmountSchema
from app.finance.service import GoalService
from app.groups.exception import UserNotFoundInGroup
from app.users.exception import AccountNotFound

router = APIRouter(prefix="/goals", tags=["goals"])

logger = logging.getLogger(__name__)


@router.post("/",
             response_model=GoalResponseSchema,
             status_code=status.HTTP_201_CREATED,
             response_model_exclude_unset=True)
async def create_goal(goal_data: GoalCreateSchema,
                      goal_service: Annotated[GoalService, Depends(get_goal_service)],
                      user_id: int = Depends(get_request_user_id)
                      ):
    """Метод для создания целей и для группы и для личных целей"""
    goal = await goal_service.create_goal(user_id=user_id, goal_user_data=goal_data)
    return goal


@router.get("/account/{account_id}",
            response_model=List[GoalResponseSchema],
            status_code=status.HTTP_200_OK,
            response_model_exclude_unset=True)
async def get_goal_by_account_id(account_id: int,
                                 goal_service: Annotated[GoalService, Depends(get_goal_service)],
                                 user_id: int = Depends(get_request_user_id)
                                 ):
    """Метод для получения целей по аккаунту"""
    try:
        goal_group = await goal_service.get_goal_by_account_id(account_id=account_id, user_id=user_id)
        return goal_group
    except AccountNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except GoalNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal_amount(goal_id: int,
                             goal_service: Annotated[GoalService, Depends(get_goal_service)],
                             user_id: int = Depends(get_request_user_id)
                             ):
    """Метод для удалении цели"""
    try:
        await goal_service.delete_goal(user_id=user_id, goal_id=goal_id)

    except GoalNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except AccessDeniedGoal as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except UserNotFoundInGroup as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except AccountNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
