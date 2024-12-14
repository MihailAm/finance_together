from fastapi import Depends, security, Security, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db_session
from app.settings import Settings
from app.users.exception import TokenExpired, TokenNotCorrect, TokenNotCorrectType
from app.users.repository import UserRepository
from app.users.service import AuthService, UserService


async def get_user_repository(db_session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return UserRepository(db_session=db_session)


async def get_auth_service(user_repository: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(setting=Settings(),
                       user_repository=user_repository)


reusable_oauth2 = security.HTTPBearer()


async def get_request_user_id(auth_service: AuthService = Depends(get_auth_service),
                              token: security.http.HTTPAuthorizationCredentials = Security(reusable_oauth2)) -> int:
    try:
        user_id = auth_service.get_user_id_from_access_token(token.credentials)

    except TokenNotCorrectType as e:
        raise HTTPException(
            status_code=401,
            detail=e.message
        )
    except TokenExpired as e:
        raise HTTPException(
            status_code=401,
            detail=e.detail
        )
    except TokenNotCorrect as e:
        raise HTTPException(
            status_code=401,
            detail=e.detail
        )

    return user_id


async def get_request_user_id_from_refresh(auth_service: AuthService = Depends(get_auth_service),
                                           token: security.http.HTTPAuthorizationCredentials = Security(
                                               reusable_oauth2)) -> int:
    try:
        user_id = auth_service.get_user_id_from_refresh_token(token.credentials)

    except TokenNotCorrectType as e:
        raise HTTPException(
            status_code=401,
            detail=e.message
        )
    except TokenExpired as e:
        raise HTTPException(
            status_code=401,
            detail=e.detail
        )
    except TokenNotCorrect as e:
        raise HTTPException(
            status_code=401,
            detail=e.detail
        )

    return user_id


async def get_user_service(user_repository: UserRepository = Depends(get_user_repository),
                           auth_service: AuthService = Depends(get_auth_service)) -> UserService:
    return UserService(user_repository=user_repository, auth_service=auth_service)
