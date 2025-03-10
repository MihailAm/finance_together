import logging
from dataclasses import dataclass

from app.finance.exception import CategoryNotFound
from app.finance.repository import CategoryRepository, CategoryCache
from app.finance.schema import CategorySchema
from app.settings import Settings

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class CategoryService:
    category_repository: CategoryRepository
    category_cache: CategoryCache

    async def create_category(self, name: str, user_id: int) -> CategorySchema:
        cat = await self.category_repository.create_category(name=name, user_id=user_id)
        await self.category_cache.delete_categories(user_id=user_id)
        return CategorySchema.model_validate(cat)

    async def get_all_categories(self, user_id: int) -> list[CategorySchema]:
        categories = await self.category_cache.get_cache_categories(user_id=user_id)
        if categories:
            return categories

        cats = await self.category_repository.get_all_categories(user_id=user_id)
        if not cats:
            raise CategoryNotFound("Категорий не найдена")

        cats = [CategorySchema.model_validate(cat) for cat in cats]
        await self.category_cache.set_cache_categories(user_id=user_id, categories=cats)

        return cats

    async def update_category_name(self, category_id: int, new_name: str, user_id: int) -> CategorySchema:
        cat = await self.category_repository.update_category_name(category_id=category_id,
                                                                  new_name=new_name,
                                                                  user_id=user_id)
        if not cat:
            raise CategoryNotFound("Категория не найдена")

        await self.category_cache.delete_categories(user_id=user_id)

        return CategorySchema.model_validate(cat)

    async def delete_category(self, category_id: int, user_id: int) -> None:
        cat = await self.get_category_by_id(category_id=category_id, user_id=user_id)
        logger.debug(f"Cat: {cat}")
        if not cat:
            raise CategoryNotFound("Категория не найдена")

        await self.category_cache.delete_categories(user_id=user_id)

        return await self.category_repository.delete_category(category_id=category_id, user_id=user_id)

    async def get_category_by_id(self, category_id: int, user_id: int) -> CategorySchema:
        cat = await self.category_repository.get_category_by_id(category_id=category_id, user_id=user_id)
        if not cat:
            raise CategoryNotFound("Категория не найдена")
        return CategorySchema.model_validate(cat)
