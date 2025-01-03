from dataclasses import dataclass

from app.groups.repository.group import GroupRepository
from app.settings import Settings


@dataclass
class GroupService:
    setting: Settings
    group_repository: GroupRepository


