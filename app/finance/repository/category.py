from dataclasses import dataclass
from typing import List

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.finance.models import Category


@dataclass
class CategoryRepository:
    db_session: AsyncSession

    async def create_category(self, name: str, user_id: int) -> Category:
        category = Category(name=name, user_id=user_id)

        async with self.db_session as session:
            session.add(category)
            await session.commit()
            return category

    async def get_all_categories(self, user_id: int) -> List[Category]:
        query = select(Category).where(Category.user_id == user_id)

        async with self.db_session as session:
            cats = (await session.execute(query)).scalars().all()
            return list(cats)

    async def update_category_name(self, category_id: int, new_name: str, user_id: int) -> Category | None:
        query = (
            update(Category)
            .where(Category.user_id == user_id, Category.id == category_id)
            .values(name=new_name)
            .returning(Category)
        )

        async with self.db_session as session:
            update_cat = (await session.execute(query)).scalar_one_or_none()
            await session.commit()
            return update_cat

    async def get_category_by_id(self, category_id: int, user_id: int) -> Category | None:
        query = select(Category).where(Category.id == category_id, Category.user_id == user_id)

        async with self.db_session as session:
            cat = (await session.execute(query)).scalar_one_or_none()
            return cat

    async def delete_category(self, category_id: int, user_id: int) -> None:
        query = delete(Category).where(Category.id == category_id, Category.user_id == user_id)
        async with self.db_session as session:
            await session.execute(query)
            await session.commit()
