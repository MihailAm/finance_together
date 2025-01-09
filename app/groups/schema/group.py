from pydantic import BaseModel, ConfigDict


class GroupSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class GroupCreateSchema(BaseModel):
    name: str
