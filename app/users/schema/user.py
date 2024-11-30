from pydantic import BaseModel, ConfigDict



class UserLoginSchema(BaseModel):
    user_id: int
    access_token: str


class UserCreateSchema(BaseModel):
    name: str
    surname: str
    password: str | bytes | None = None
    email: str

    model_config = ConfigDict(from_attributes=True)


class UserCreateSchemaOAuth(BaseModel):
    name: str
    surname: str
    password: str | bytes | None = None
    email: str
    google_access_token: str | None = None
    yandex_access_token: str | None = None