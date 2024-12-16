from pydantic import BaseModel, ConfigDict, Field


class UserLoginSchema(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class UserCreateSchema(BaseModel):
    name: str
    surname: str
    password: str | bytes | None = None
    email: str

    model_config = ConfigDict(from_attributes=True)


class UserCreateSchemaOAuth(UserCreateSchema):
    google_access_token: str | None = None
    yandex_access_token: str | None = None
