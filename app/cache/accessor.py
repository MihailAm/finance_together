import redis.asyncio as redis

from app.settings import Settings


async  def get_redis_connection() -> redis.Redis:
    settings = Settings()
    return await redis.from_url(
        f"redis://{settings.CACHE_HOST}:{settings.CACHE_PORT}/{settings.CACHE_DB}",
        encoding="utf-8",
        decode_responses=True
    )