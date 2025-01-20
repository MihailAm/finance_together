from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from app.users.exception import UserNotFoundException, PasswordValidationError
from app.users.schema import UserLoginSchema, UserCreateSchema, UserSchema
from app.users.service import UserService
from app.dependecy import get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post('/', response_model=UserLoginSchema)
async def create_user(body: UserCreateSchema, user_service: Annotated[UserService, Depends(get_user_service)]):
    try:
        new_user = await user_service.create_user(body.name, body.surname, body.email, body.password)
        return new_user
    except PasswordValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message
        )


@router.get('/{user_id}', response_model=UserSchema)
async def create_user(user_id: int, user_service: Annotated[UserService, Depends(get_user_service)]):
    try:
        new_user = await user_service.get_user(user_id=user_id)
        return new_user
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
