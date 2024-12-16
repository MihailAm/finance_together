from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse

from app.dependecy import get_auth_service, get_request_user_id, get_user_repository, get_request_user_id_from_refresh
from app.users.exception import UserNotFoundException, UserNotCorrectPasswordException
from app.users.repository import UserRepository
from app.users.schema import UserLoginSchema, AuthJwtSchema, UserCreateSchema
from app.users.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    '/login/',
    response_model=UserLoginSchema)
async def login(body: AuthJwtSchema,
                auth_service: Annotated[AuthService, Depends(get_auth_service)]):
    try:
        return await auth_service.login(body.email, body.password)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=404,
            detail=e.detail
        )
    except UserNotCorrectPasswordException as e:
        raise HTTPException(
            status_code=401,
            detail=e.detail
        )


@router.post('/refresh/',
             response_model=UserLoginSchema,
             response_model_exclude_none=True)
async def auth_refresh_jwt(auth_service: Annotated[AuthService, Depends(get_auth_service)],
                           user_id: int = Depends(get_request_user_id_from_refresh)):
    access_token = await auth_service.generate_access_token(user_id=user_id)
    return UserLoginSchema(access_token=access_token)


@router.get('tests', response_model=UserCreateSchema)
async def test(user_rep: Annotated[UserRepository, Depends(get_user_repository)],
               user_id: int = Depends(get_request_user_id)):
    return await user_rep.get_user(user_id=user_id)


@router.get('/login/google',
            response_class=RedirectResponse)
async def google_client(auth_service: Annotated[AuthService, Depends(get_auth_service)]):
    redirect_url = auth_service.get_google_redirect_url()
    print(redirect_url)
    return RedirectResponse(redirect_url)


@router.get('/google')
async def google_auth(
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        code: str
):
    return await auth_service.google_auth(code=code)
