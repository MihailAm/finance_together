from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class GroupRepository:
    db_session: AsyncSession