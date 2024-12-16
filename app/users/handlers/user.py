from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from app.users.schema import UserLoginSchema, UserCreateSchema
from app.users.service import UserService
from app.dependecy import get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post('/', response_model=UserLoginSchema)
async def create_user(body: UserCreateSchema, user_service: Annotated[UserService, Depends(get_user_service)]):
    new_user = await user_service.create_user(body.name, body.surname, body.email, body.password)
    return new_user
