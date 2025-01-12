import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends, status, HTTPException

from app.dependecy import get_request_user_id, get_goal_service
from app.finance.exception import GoalNotFound, AccessDeniedGoal
from app.finance.schema import GoalResponseSchema, GoalUserCreateSchema, GoalGroupCreateSchema, GoalUpdateAmountSchema
from app.finance.service import GoalService
from app.groups.exception import UserNotFoundInGroup

router = APIRouter(prefix="/goals", tags=["goals"])

logger = logging.getLogger(__name__)

@router.post("/user",
             response_model=GoalResponseSchema,
             status_code=status.HTTP_201_CREATED,
             response_model_exclude_unset=True)
async def create_goal_users(goal_data: GoalUserCreateSchema,
                            goal_service: Annotated[GoalService, Depends(get_goal_service)],
                            user_id: int = Depends(get_request_user_id)
                            ):
    """Метод для создания личных целей"""
    goal = await goal_service.create_goal(user_id=user_id, goal_user_data=goal_data)
    return goal


@router.post("/group",
             response_model=GoalResponseSchema,
             status_code=status.HTTP_201_CREATED,
             response_model_exclude_unset=True)
async def create_goal_group(goal_data: GoalGroupCreateSchema,
                            goal_service: Annotated[GoalService, Depends(get_goal_service)],
                            user_id: int = Depends(get_request_user_id)
                            ):
    """Метод для создания групповых целей"""
    try:
        goal = await goal_service.create_goal(user_id=user_id, goal_group_data=goal_data)
        return goal
    except UserNotFoundInGroup as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


@router.get("/group/{group_id}",
            response_model=List[GoalResponseSchema],
            status_code=status.HTTP_200_OK,
            response_model_exclude_unset=True)
async def get_goal_by_group_id(group_id: int,
                               goal_service: Annotated[GoalService, Depends(get_goal_service)],
                               user_id: int = Depends(get_request_user_id)
                               ):
    """Метод для получения групповых целей"""
    try:
        goal_group = await goal_service.get_goal_by_group_id(group_id=group_id, user_id=user_id)
        return goal_group
    except UserNotFoundInGroup as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except GoalNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


@router.get("/user",
            response_model=List[GoalResponseSchema])
async def get_goal_by_user_id(goal_service: Annotated[GoalService, Depends(get_goal_service)],
                              user_id: int = Depends(get_request_user_id)
                              ):
    """Метод для получения личных целей"""
    try:
        goal_user = await goal_service.get_goal_by_user_id(user_id=user_id)
        return goal_user
    except GoalNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


@router.patch("/update/amount",
              response_model=GoalResponseSchema,
              status_code=status.HTTP_200_OK,
              response_model_exclude_unset=True)
async def update_goal_amount(update_data: GoalUpdateAmountSchema,
                             goal_service: Annotated[GoalService, Depends(get_goal_service)],
                             user_id: int = Depends(get_request_user_id)
                             ):
    """Метод для обновления суммы"""
    try:
        goal = await goal_service.update_goal_amount(user_id=user_id, update_data=update_data)
        return goal
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


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_goal_amount(goal_id: int,
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
