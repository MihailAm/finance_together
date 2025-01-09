import httpx
from fastapi import Depends, security, Security, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.groups.repository import GroupMemberRepository, GroupRepository
from app.groups.service import GroupService
from app.groups.service.group_member import GroupMemberService
from app.infrastructure.database import get_db_session
from app.settings import Settings
from app.users.client import GoogleClient
from app.users.client.yandex import YandexClient
from app.users.exception import TokenExpired, TokenNotCorrect, TokenNotCorrectType
from app.users.repository import UserRepository, AccountRepository
from app.users.service import AuthService, UserService, AccountService


async def get_user_repository(db_session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return UserRepository(db_session=db_session)


async def get_async_client() -> httpx.AsyncClient:
    return httpx.AsyncClient()


async def get_google_client(async_client: httpx.AsyncClient = Depends(get_async_client)) -> GoogleClient:
    return GoogleClient(settings=Settings(), async_client=async_client)


async def get_yandex_client(async_client: httpx.AsyncClient = Depends(get_async_client)) -> YandexClient:
    return YandexClient(settings=Settings(), async_client=async_client)


async def get_auth_service(user_repository: UserRepository = Depends(get_user_repository),
                           google_client: GoogleClient = Depends(get_google_client),
                           yandex_client: YandexClient = Depends(get_yandex_client)) -> AuthService:
    return AuthService(setting=Settings(),
                       user_repository=user_repository,
                       google_client=google_client,
                       yandex_client=yandex_client)


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


async def get_group_member_repository(db_session: AsyncSession = Depends(get_db_session)) -> GroupMemberRepository:
    return GroupMemberRepository(db_session=db_session)


async def get_group_member_service(
        group_member_repository: GroupMemberRepository = Depends(get_group_member_repository),
        user_service: UserService = Depends(get_user_service)) -> GroupMemberService:
    return GroupMemberService(setting=Settings(),
                              group_member_repository=group_member_repository,
                              user_profile_service=user_service)


async def get_account_repository(db_session: AsyncSession = Depends(get_db_session)) -> AccountRepository:
    return AccountRepository(db_session=db_session)


async def get_account_service(
        account_repository: AccountRepository = Depends(get_account_repository),
        group_member_service: GroupMemberService = Depends(get_group_member_service)) -> AccountService:
    return AccountService(setting=Settings(),
                          account_repository=account_repository,
                          group_member_service=group_member_service)


async def get_group_repository(db_session: AsyncSession = Depends(get_db_session)) -> GroupRepository:
    return GroupRepository(db_session=db_session)


async def get_group_service(group_repository: GroupRepository = Depends(get_group_repository),
                            group_member_repository: GroupMemberService = Depends(
                                get_group_member_service)) -> GroupService:
    return GroupService(setting=Settings(),
                        group_repository=group_repository,
                        group_member_service=group_member_repository)
