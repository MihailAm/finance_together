from typing import Annotated, List

from fastapi import APIRouter, status, Depends, HTTPException

from app.dependecy import get_request_user_id, get_goal_contributions_service
from app.finance.exception import GoalNotFound, AccessDeniedGoal, GoalContribForbidden, GoalContribNotFound
from app.finance.schema import CreateGoalContributionSchema, ResponseGoalContributionSchema, UpdateGoalContributionFlag
from app.finance.service import GoalContributionsService
from app.groups.exception import UserNotFoundInGroup
from app.users.exception import AccountNotFound

router = APIRouter(prefix="/goals/contributions", tags=["goal_contributions"])


@router.post("/",
             response_model=ResponseGoalContributionSchema,
             status_code=status.HTTP_201_CREATED,
             response_model_exclude_unset=True)
async def create_goal_contrib(goal_data: CreateGoalContributionSchema,
                              goal_contributions_service:
                              Annotated[GoalContributionsService, Depends(get_goal_contributions_service)],
                              user_id: int = Depends(get_request_user_id)
                              ):
    """Метод для создании пополнения цели и ее изменение"""
    try:
        goal_contrib = await goal_contributions_service.create_goal_contributions(user_id=user_id,
                                                                                  goal_contrib_user_data=goal_data)
        return goal_contrib

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


@router.get("/{goal_id}",
            response_model=List[ResponseGoalContributionSchema],
            status_code=status.HTTP_200_OK)
async def get_goal_contrib_by_user_goal_id(goal_id: int,
                                           goal_contributions_service: Annotated[
                                               GoalContributionsService, Depends(get_goal_contributions_service)],
                                           user_id: int = Depends(get_request_user_id)):
    """Метод для получении истории пополнения целей"""
    try:
        goal_contributions = await goal_contributions_service.get_goal_contributions_by_user_goal_id(goal_id=goal_id,
                                                                                                     user_id=user_id)
        return goal_contributions
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
    except AccountNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except AccessDeniedGoal as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )


@router.get("/operation/{goal_contrib_id}",
            response_model=ResponseGoalContributionSchema,
            status_code=status.HTTP_200_OK)
async def get_goal_contrib_by_id(goal_contrib_id: int,
                                 goal_contributions_service: Annotated[
                                     GoalContributionsService, Depends(get_goal_contributions_service)],
                                 ):
    """Метод для получении цели по идентификатору"""
    try:
        goal_contributions = await goal_contributions_service.get_goal_contrib_by_id(goal_contrib_id=goal_contrib_id)
        return goal_contributions
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
    except AccountNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except AccessDeniedGoal as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )


@router.patch("/{contribution_id}/toggle-active-pay",
              response_model=ResponseGoalContributionSchema,
              status_code=status.HTTP_200_OK)
async def toggle_is_active_pay(contribution_id: int,
                               is_active_pay_data: UpdateGoalContributionFlag,
                               goal_contributions_service: Annotated[
                                   GoalContributionsService, Depends(get_goal_contributions_service)],
                               user_id: int = Depends(get_request_user_id)):
    """Метод для получении истории пополнения целей"""

    try:
        goal_contrib = await goal_contributions_service.toggle_is_active_pay(contribution_id=contribution_id,
                                                                             is_active_pay=is_active_pay_data.is_active_pay,
                                                                             user_id=user_id)
        return goal_contrib
    except GoalContribForbidden as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except GoalContribNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
