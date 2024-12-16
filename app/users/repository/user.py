from dataclasses import dataclass

from pydantic import EmailStr
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import UserProfile
from app.users.schema import UserCreateSchema


@dataclass
class UserRepository:
    db_session: AsyncSession

    async def create_user(self, user: UserCreateSchema) -> UserProfile:
        query = insert(UserProfile).values(**user.model_dump()).returning(UserProfile.id)

        async with self.db_session as session:
            user_id: int = (await session.execute(query)).scalar()
            await session.commit()
            return await self.get_user(user_id)

    async def get_user(self, user_id: int) -> UserProfile | None:
        query = select(UserProfile).where(UserProfile.id == user_id)

        async with self.db_session as session:
            user = (await session.execute(query)).scalar_one_or_none()
            return user

    async def get_user_by_email(self, email: EmailStr) -> UserProfile | None:
        query = select(UserProfile).where(UserProfile.email == email)

        async with self.db_session as session:
            user = (await session.execute(query)).scalar_one_or_none()
            return user
