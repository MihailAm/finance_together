from typing import Annotated, List

from fastapi import APIRouter, Depends, status, HTTPException

from app.dependecy import get_request_user_id, get_group_member_service
from app.groups.exception import GroupNotFound, UserNotFoundInGroup, AccessDenied
from app.groups.models.group_member import RoleEnum
from app.groups.schema import UserGroupResponse
from app.groups.schema.group_member import AddMemberSchema, GroupMemberSchema, DeleteMemberSchema, ChangeMemberSchema
from app.groups.service import GroupMemberService
from app.users.exception import UserNotFoundException

router = APIRouter(prefix="/group_members", tags=["group_members"])


@router.get("/", response_model=List[UserGroupResponse])
async def get_groups_user(group_member_service: Annotated[GroupMemberService, Depends(get_group_member_service)],
                          user_id: int = Depends(get_request_user_id)
                          ):
    """Метод для получения всех групп пользователя"""
    try:
        groups = await group_member_service.get_groups_user(user_id=user_id)
        return groups
    except GroupNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


@router.post("/members/add", response_model=GroupMemberSchema, status_code=status.HTTP_201_CREATED)
async def add_member(group_member_service: Annotated[GroupMemberService, Depends(get_group_member_service)],
                     body: AddMemberSchema,
                     user_id: int = Depends(get_request_user_id)
                     ):
    """Метод для добавления участника в группу"""
    try:
        member = await group_member_service.add_member(member=body, user_id=user_id)
        return member
    except UserNotFoundInGroup as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


@router.delete("/members/delete", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(group_member_service: Annotated[GroupMemberService, Depends(get_group_member_service)],
                        body: DeleteMemberSchema,
                        user_id: int = Depends(get_request_user_id)
                        ):
    """Метод для удаления участника группы"""
    try:
        await group_member_service.remove_member(member=body, user_id=user_id)
    except UserNotFoundInGroup as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except AccessDenied as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )


@router.patch("/change/role", response_model=GroupMemberSchema, status_code=status.HTTP_200_OK)
async def change_member_role(group_member_service: Annotated[GroupMemberService, Depends(get_group_member_service)],
                             body: ChangeMemberSchema,
                             user_id: int = Depends(get_request_user_id)
                             ):
    """Метод для смены роли участника"""
    try:
        group_member = await group_member_service.change_role(body=body, user_id=user_id)
        return group_member
    except UserNotFoundInGroup as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except AccessDenied as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )


@router.get("/{group_id}/members")
async def get_group_members(group_member_service: Annotated[GroupMemberService, Depends(get_group_member_service)],
                            group_id: int,
                            user_id: int = Depends(get_request_user_id)
                            ):
    """Метод для получение всех участников группы"""
    try:
        members_group = await group_member_service.get_members_group(group_id=group_id, user_id=user_id)
        return members_group
    except UserNotFoundInGroup as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
