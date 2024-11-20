from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.settings import Settings

settings = Settings()
engine = create_async_engine(settings.db_url, future=True, echo=True, pool_pre_ping=True)

AsyncSessionFactory = async_sessionmaker(
    engine,
    autoflush=False,
    expire_on_commit=False
)


async def get_db_session() -> AsyncSessionFactory:
    async with AsyncSessionFactory() as session:
        yield session


Base = declarative_base()
