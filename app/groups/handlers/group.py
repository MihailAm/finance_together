from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException

from app.dependecy import get_request_user_id, get_group_service
from app.groups.exception import GroupNotFound, AccessDenied, UserNotFoundInGroup
from app.groups.schema import GroupSchema, GroupCreateSchema
from app.groups.service import GroupService

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/", response_model=GroupSchema, status_code=status.HTTP_201_CREATED)
async def create_group(group_service: Annotated[GroupService, Depends(get_group_service)],
                       body: GroupCreateSchema,
                       user_id: int = Depends(get_request_user_id),
                       ):
    """Метод для создания группы"""
    group_result = await group_service.create_group(name=body.name, user_id=user_id)
    return group_result


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(group_service: Annotated[GroupService, Depends(get_group_service)],
                       group_id: int,
                       user_id: int = Depends(get_request_user_id),
                       ):
    """Метод для удаления группы"""
    try:
        await group_service.delete_group(group_id=group_id, user_id=user_id)

    except GroupNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except AccessDenied as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except UserNotFoundInGroup as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )



@router.get("/{group_id}", response_model=GroupSchema)
async def get_group_info(group_service: Annotated[GroupService, Depends(get_group_service)],
                         group_id: int,
                         user_id: int = Depends(get_request_user_id)
                         ):
    """Метод для получения информации о группе"""
    try:
        group_result = await group_service.get_group_info(group_id=group_id, user_id=user_id)
        return group_result
    except GroupNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except UserNotFoundInGroup as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
