import httpx
from fastapi import Depends, security, Security, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.cron.goal import CronJobGoal
from app.finance.repository import TransactionRepository, PlannedExpensesRepository, GoalRepository, DebtRepository, \
    GoalContributionsRepository
from app.finance.repository.category import CategoryRepository
from app.finance.service import TransactionService, PlannedExpensesService, GoalService, DebtService, \
    GoalContributionsService
from app.finance.service.category import CategoryService
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
    return GroupMemberService(
        group_member_repository=group_member_repository,
        user_profile_service=user_service
    )


async def get_account_repository(db_session: AsyncSession = Depends(get_db_session)) -> AccountRepository:
    return AccountRepository(db_session=db_session)


async def get_account_service(
        account_repository: AccountRepository = Depends(get_account_repository),
        group_member_service: GroupMemberService = Depends(get_group_member_service)) -> AccountService:
    return AccountService(account_repository=account_repository,
                          group_member_service=group_member_service)


async def get_group_repository(db_session: AsyncSession = Depends(get_db_session)) -> GroupRepository:
    return GroupRepository(db_session=db_session)


async def get_group_service(group_repository: GroupRepository = Depends(get_group_repository),
                            group_member_repository: GroupMemberService = Depends(
                                get_group_member_service)) -> GroupService:
    return GroupService(setting=Settings(),
                        group_repository=group_repository,
                        group_member_service=group_member_repository)


async def get_category_repository(db_session: AsyncSession = Depends(get_db_session)) -> CategoryRepository:
    return CategoryRepository(db_session=db_session)


async def get_category_service(
        category_repository: CategoryRepository = Depends(get_category_repository)) -> CategoryService:
    return CategoryService(setting=Settings(),
                           category_repository=category_repository,
                           )


async def get_transaction_repository(db_session: AsyncSession = Depends(get_db_session)) -> TransactionRepository:
    return TransactionRepository(db_session=db_session)


async def get_transaction_service(
        transaction_repository: TransactionRepository = Depends(get_transaction_repository),
        account_service: AccountService = Depends(get_account_service)
) -> TransactionService:
    return TransactionService(transaction_repository=transaction_repository,
                              account_service=account_service
                              )


async def get_planned_expenses_repository(
        db_session: AsyncSession = Depends(get_db_session)) -> PlannedExpensesRepository:
    return PlannedExpensesRepository(db_session=db_session)


async def get_planned_expenses_service(
        planned_expenses_repository: PlannedExpensesRepository = Depends(get_planned_expenses_repository),
        group_member_service: GroupMemberService = Depends(get_group_member_service),
        account_service: AccountService = Depends(get_account_service)
) -> PlannedExpensesService:
    return PlannedExpensesService(planned_expenses_repository=planned_expenses_repository,
                                  group_member_service=group_member_service,
                                  account_service=account_service
                                  )


async def get_goal_repository(
        db_session: AsyncSession = Depends(get_db_session)) -> GoalRepository:
    return GoalRepository(db_session=db_session)


async def get_goal_service(
        goal_repository: GoalRepository = Depends(get_goal_repository),
        group_member_service: GroupMemberService = Depends(get_group_member_service),
        account_service: AccountService = Depends(get_account_service)
) -> GoalService:
    return GoalService(goal_repository=goal_repository,
                       group_member_service=group_member_service,
                       account_service=account_service
                       )


async def get_debt_repository(
        db_session: AsyncSession = Depends(get_db_session)) -> DebtRepository:
    return DebtRepository(db_session=db_session)


async def get_debt_service(
        debt_repository: DebtRepository = Depends(get_debt_repository)) -> DebtService:
    return DebtService(debt_repository=debt_repository)


async def get_goal_contributions_repository(
        db_session: AsyncSession = Depends(get_db_session)) -> GoalContributionsRepository:
    return GoalContributionsRepository(db_session=db_session)


async def get_goal_contributions_service(
        goal_service: GoalService = Depends(get_goal_service),
        goal_contribution_repository: GoalContributionsRepository = Depends(get_goal_contributions_repository),
        account_service: AccountService = Depends(get_account_service),
        group_member_service: GroupMemberService = Depends(get_group_member_service),
) -> GoalContributionsService:
    return GoalContributionsService(goal_service=goal_service,
                                    goal_contribution_repository=goal_contribution_repository,
                                    account_service=account_service,
                                    group_member_service=group_member_service)


async def get_cron_job_goal() -> CronJobGoal:
    return CronJobGoal()
