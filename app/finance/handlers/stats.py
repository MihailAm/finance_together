from datetime import datetime
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependecy import get_request_user_id, get_stats_service, get_planned_expenses_service
from app.finance.exception import TransactionNotFound, PlannedExpensesNotFound
from app.finance.schema import StatTransactionSchema, PlannedExpensesResponseSchema, PlannedExpensesStats
from app.finance.service import StatsService, PlannedExpensesService
from app.users.exception import AccountNotFound

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/account/{account_id}", response_model=List[StatTransactionSchema])
async def get_transactions(account_id: int,
                           start_date: datetime,
                           end_date: datetime,
                           stat_service: Annotated[StatsService, Depends(get_stats_service)],
                           user_id: int = Depends(get_request_user_id)):
    """Метод для получений транзакций аккаунта"""
    try:
        transactions = await stat_service.get_stats_transactions(account_id=account_id,
                                                                 start_date=start_date,
                                                                 end_date=end_date,
                                                                 user_id=user_id)
        return transactions
    except AccountNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except TransactionNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


@router.get("/planned_expenses/account/{account_id}", response_model=List[PlannedExpensesStats])
async def get_planned_expenses(account_id: int,
                               dur_date: datetime,
                               stat_service: Annotated[StatsService, Depends(get_stats_service)],
                               user_id: int = Depends(get_request_user_id)):
    """Метод для получения планирования финансов для аккаунта"""
    try:
        planned_expenses = await stat_service.get_planned_expenses(account_id=account_id, user_id=user_id,
                                                                   dur_date=dur_date)
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
