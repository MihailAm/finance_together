from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from app.dependecy import get_request_user_id, get_account_service
from app.groups.exception import UserNotFoundInGroup
from app.users.exception import AccountNotFound, GroupAccountConflictException, AccountAccessError
from app.users.schema import AccountSchema, AccountCreateSchemaUser, DepositRequest
from app.users.service import AccountService

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get('/user', response_model=list[AccountSchema], response_model_exclude_unset=True)
async def all_user_accounts(account_service: Annotated[AccountService, Depends(get_account_service)],
                            user_id: int = Depends(get_request_user_id)):
    """Метод для получения всех личных аккаунтов"""
    try:
        accounts = await account_service.all_accounts(user_id=user_id)
        return accounts
    except AccountNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


@router.post("/user", response_model=AccountSchema, response_model_exclude_unset=True)
async def create_user_account(body: AccountCreateSchemaUser,
                              account_service: Annotated[AccountService, Depends(get_account_service)],
                              user_id: int = Depends(get_request_user_id)):
    """Метод для создания личного аккаунта"""
    account = await account_service.create_user_account(body=body, user_id=user_id)

    return account


@router.post("/group/{group_id}", response_model=AccountSchema, response_model_exclude_unset=True)
async def create_group_account(group_id: int,
                               body: AccountCreateSchemaUser,
                               account_service: Annotated[AccountService, Depends(get_account_service)],
                               ):
    """Метод для создания аккаунта группы"""
    try:
        account = await account_service.create_group_account(body=body, group_id=group_id)
        return account
    except GroupAccountConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )


@router.get('/group/{group_id}', response_model=AccountSchema, response_model_exclude_unset=True)
async def group_account(group_id: int,
                        account_service: Annotated[AccountService, Depends(get_account_service)],
                        user_id: int = Depends(get_request_user_id)):
    """Метод для получения аккаунта группы"""
    try:
        accounts = await account_service.get_group_account(group_id=group_id, user_id=user_id)
        return accounts
    except AccountNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except UserNotFoundInGroup as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )


@router.patch("/{account_id}", response_model=AccountSchema)
async def rename_account(account_id: int,
                         account_name: str,
                         account_service: Annotated[AccountService, Depends(get_account_service)],
                         user_id: int = Depends(get_request_user_id)):
    """Метод для изменения имени аккаунта"""
    try:
        update_task = await account_service.update_account_name(account_id=account_id, account_name=account_name,
                                                                user_id=user_id)
        return update_task
    except AccountNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


@router.patch("/{account_id}/deposit", response_model=AccountSchema)
async def deposit_account(deposit: DepositRequest,
                          account_service: Annotated[AccountService, Depends(get_account_service)],
                          user_id: int = Depends(get_request_user_id)):
    """Метод для пополнения баланса"""
    try:
        return await account_service.deposit_account(account_id=deposit.account_id,
                                                     amount=deposit.amount,
                                                     user_id=user_id)
    except AccountNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аккаунт не существует или не является ни личным, ни групповым",
        )
    except AccountAccessError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет доступа к этому аккаунту",
        )
    except UserNotFoundInGroup as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.patch("/{account_id}/withdraw", response_model=AccountSchema)
async def withdraw_account(deposit: DepositRequest,
                           account_service: Annotated[AccountService, Depends(get_account_service)],
                           user_id: int = Depends(get_request_user_id)):
    """Метод для списание денег с баланса"""
    try:
        return await account_service.withdraw_account(account_id=deposit.account_id,
                                                      amount=deposit.amount,
                                                      user_id=user_id)
    except AccountNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аккаунт не существует или не является ни личным, ни групповым",
        )
    except AccountAccessError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет доступа к этому аккаунту",
        )
    except UserNotFoundInGroup as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
