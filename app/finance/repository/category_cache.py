import json
from dataclasses import dataclass

from redis.asyncio.client import Redis

from app.finance.schema import CategorySchema


@dataclass
class CategoryCache:
    redis: Redis

    async def get_cache_categories(self, user_id: int) -> list[CategorySchema]:
        """Получает категории из кэша"""
        cache_key = f"categories:{user_id}"
        categories_json = await self.redis.lrange(cache_key, 0, -1)
        return [CategorySchema.model_validate(json.loads(cat)) for cat in categories_json]

    async def set_cache_categories(self, user_id: int, categories: list[CategorySchema]):
        """Сохраняет категории в кэше"""
        cache_key = f"categories:{user_id}"
        categories_json = [cat.model_dump_json() for cat in categories]
        await self.redis.delete(cache_key)
        await self.redis.lpush(cache_key, *categories_json)

    async def delete_categories(self, user_id: int):
        """Удаляет категории из кэша"""
        await self.redis.delete(f"categories:{user_id}")
