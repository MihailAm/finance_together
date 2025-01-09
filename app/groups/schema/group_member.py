from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.groups.models.group_member import RoleEnum


class UserGroupResponse(BaseModel):
    id: int
    user_id: int
    group_name: str
    role: str
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GroupMemberSchema(BaseModel):
    id: int
    user_id: int
    group_id: int
    role: str
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AddMemberSchema(BaseModel):
    group_id: int
    email: EmailStr
    role: RoleEnum = RoleEnum.MEMBER

    model_config = ConfigDict(from_attributes=True)


class DeleteMemberSchema(BaseModel):
    member_id: int
    group_id: int

    model_config = ConfigDict(from_attributes=True)


class ChangeMemberSchema(BaseModel):
    user_id: int
    group_id: int
    role: RoleEnum
