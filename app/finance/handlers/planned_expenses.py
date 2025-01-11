from typing import Annotated, List

from fastapi import APIRouter, status, Depends, HTTPException

from app.dependecy import get_request_user_id, get_planned_expenses_service
from app.finance.exception import PlannedExpensesNotFound
from app.finance.schema import PlannedExpensesResponseSchema, PlannedExpensesCreateSchema
from app.finance.service import PlannedExpensesService
from app.groups.exception import AccessDenied, UserNotFoundInGroup
from app.users.exception import AccountNotFound

router = APIRouter(prefix="/planned_expenses", tags=["planned_expenses"])


@router.post("/", response_model=PlannedExpensesResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_planned_expenses(planned_expenses_data: PlannedExpensesCreateSchema,
                                  planned_expenses_service:
                                  Annotated[PlannedExpensesService, Depends(get_planned_expenses_service)],
                                  user_id: int = Depends(get_request_user_id)
                                  ):
    """Метод для создания плановой операции"""
    try:
        planned_expenses = await planned_expenses_service.create_planned_expenses(
            planned_expenses_data=planned_expenses_data,
            user_id=user_id
        )
        return planned_expenses
    except AccessDenied as e:
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


@router.get("/account/{account_id}", response_model=List[PlannedExpensesResponseSchema])
async def get_planned_expenses(account_id: int,
                               planned_expenses_service:
                               Annotated[PlannedExpensesService, Depends(get_planned_expenses_service)],
                               user_id: int = Depends(get_request_user_id)):
    """Метод для получения планирования финансов для аккаунта"""
    try:
        planned_expenses = await planned_expenses_service.get_planned_expenses(account_id=account_id, user_id=user_id)
        return planned_expenses
    except AccountNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except PlannedExpensesNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


@router.delete("/{planned_expenses_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_planned_expenses(planned_expenses_id: int,
                                  planned_expenses_service:
                                  Annotated[PlannedExpensesService, Depends(get_planned_expenses_service)],
                                  user_id: int = Depends(get_request_user_id)
                                  ):
    """Метод для удаления транзакции"""
    try:
        await planned_expenses_service.delete_planned_expenses(planned_expenses_id=planned_expenses_id, user_id=user_id)
    except PlannedExpensesNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except AccessDenied as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except AccountNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
