from typing import Annotated, List

from fastapi import APIRouter, status, Depends, HTTPException

from app.dependecy import get_request_user_id, get_debt_service
from app.finance.exception import DebtNotFound, AccessDeniedDebt
from app.finance.schema import DebtResponseSchema, DebtCreateSchema, DebtUpdateAmountSchema
from app.finance.service import DebtService

router = APIRouter(prefix="/debts", tags=["debts"])


@router.post("/",
             response_model=DebtResponseSchema,
             status_code=status.HTTP_201_CREATED,
             response_model_exclude_unset=True)
async def create_debt(debt_data: DebtCreateSchema,
                      debt_service: Annotated[DebtService, Depends(get_debt_service)],
                      user_id: int = Depends(get_request_user_id)
                      ):
    """Метод для создания долгов"""
    debt = await debt_service.create_debt(user_id=user_id, debt_user_data=debt_data)
    return debt


@router.get("/user",
            response_model=List[DebtResponseSchema],
            status_code=status.HTTP_200_OK,
            response_model_exclude_unset=True)
async def get_debt_by_user_id(
        debt_service: Annotated[DebtService, Depends(get_debt_service)],
        user_id: int = Depends(get_request_user_id)
):
    """Метод для получения долгов"""
    try:
        debts = await debt_service.get_debt_by_user_id(user_id=user_id)
        return debts

    except DebtNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


@router.patch("/update/amount",
              response_model=DebtResponseSchema,
              status_code=status.HTTP_200_OK,
              response_model_exclude_unset=True)
async def update_goal_amount(update_data: DebtUpdateAmountSchema,
                             debt_service: Annotated[DebtService, Depends(get_debt_service)],
                             user_id: int = Depends(get_request_user_id)
                             ):
    """Метод для обновления суммы долга"""
    try:
        debt = await debt_service.update_debt_amount(user_id=user_id, update_data=update_data)
        return debt
    except DebtNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except AccessDeniedDebt as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )


@router.delete("/{debt_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Debt Amount")
async def update_debt_amount(debt_id: int,
                             debt_service: Annotated[DebtService, Depends(get_debt_service)],
                             user_id: int = Depends(get_request_user_id)
                             ):
    """Метод для удаления долга"""
    try:
        await debt_service.delete_debt(user_id=user_id, debt_id=debt_id)

    except DebtNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except AccessDeniedDebt as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
