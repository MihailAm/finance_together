from typing import Annotated, List

from fastapi import APIRouter, Depends, status, HTTPException

from app.dependecy import get_request_user_id, get_transaction_service
from app.finance.exception import TransactionNotFound, AccessDeniedTransaction
from app.finance.schema import TransactionResponseSchema, CreateTransactionSchema
from app.finance.service import TransactionService
from app.groups.exception import AccessDenied, UserNotFoundInGroup
from app.users.exception import AccountNotFound

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=TransactionResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_transaction(transaction_data: CreateTransactionSchema,
                             transaction_service: Annotated[TransactionService, Depends(get_transaction_service)],
                             user_id: int = Depends(get_request_user_id)
                             ):
    """Метод для создания транзакции"""
    try:
        transaction = await transaction_service.create_transaction(transaction_data=transaction_data, user_id=user_id)
        return transaction
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


@router.get("/account/{account_id}", response_model=List[TransactionResponseSchema])
async def get_transactions(account_id: int,
                           transaction_service: Annotated[TransactionService, Depends(get_transaction_service)],
                           user_id: int = Depends(get_request_user_id)):
    """Метод для получений транзакций аккаунта"""
    try:
        transactions = await transaction_service.get_transactions(account_id=account_id, user_id=user_id)
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


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(transaction_id: int,
                             transaction_service: Annotated[TransactionService, Depends(get_transaction_service)],
                             user_id: int = Depends(get_request_user_id)
                             ):
    """Метод для удаления транзакции"""
    try:
        await transaction_service.delete_transaction(transaction_id=transaction_id, user_id=user_id)
    except TransactionNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except AccessDeniedTransaction as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except AccountNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
