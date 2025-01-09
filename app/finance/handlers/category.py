from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Annotated

from app.dependecy import get_request_user_id, get_category_service
from app.finance.exception import CategoryNotFound
from app.finance.schema import CategorySchema, OperationCategorySchema
from app.finance.service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(body: OperationCategorySchema,
                          category_service: Annotated[CategoryService, Depends(get_category_service)],
                          user_id: int = Depends(get_request_user_id),
                          ):
    return await category_service.create_category(name=body.name, user_id=user_id)


@router.get("/", response_model=List[CategorySchema])
async def get_all_categories(category_service: Annotated[CategoryService, Depends(get_category_service)],
                             user_id: int = Depends(get_request_user_id)
                             ):
    try:
        cats = await category_service.get_all_categories(user_id=user_id)
        return cats
    except CategoryNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


@router.get("/{category_id}", response_model=CategorySchema)
async def get_category_by_id(category_id: int,
                             category_service: Annotated[CategoryService, Depends(get_category_service)],
                             user_id: int = Depends(get_request_user_id)
                             ):
    try:
        cat = await category_service.get_category_by_id(category_id=category_id, user_id=user_id)
        return cat
    except CategoryNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


@router.put("/{category_id}", response_model=CategorySchema, status_code=status.HTTP_200_OK)
async def update_category_name(category_id: int,
                               body: OperationCategorySchema,
                               category_service: Annotated[CategoryService, Depends(get_category_service)],
                               user_id: int = Depends(get_request_user_id),

                               ):
    try:
        category = await category_service.update_category_name(category_id=category_id, new_name=body.name,
                                                               user_id=user_id)
        return category
    except CategoryNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int,
                          category_service: Annotated[CategoryService, Depends(get_category_service)],
                          user_id: int = Depends(get_request_user_id)
                          ):
    try:
        await category_service.delete_category(category_id=category_id, user_id=user_id)
    except CategoryNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
