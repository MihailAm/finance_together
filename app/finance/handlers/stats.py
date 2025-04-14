from datetime import datetime
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependecy import get_request_user_id, get_stats_service
from app.finance.exception import TransactionNotFound
from app.finance.schema import StatTransactionSchema
from app.finance.service import StatsService
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
