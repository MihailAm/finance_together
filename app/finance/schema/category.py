from pydantic import BaseModel, ConfigDict


class CategorySchema(BaseModel):
    id: int
    name: str
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class OperationCategorySchema(BaseModel):
    name: str
