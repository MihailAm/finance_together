from pydantic import BaseModel, EmailStr, Field


class AuthJwtSchema(BaseModel):
    email: EmailStr
    password: str | bytes


class GoogleUserData(BaseModel):
    id: int
    name: str = Field(alias="given_name")
    surname: str = Field(alias="family_name")
    email: str
    access_token: str


class YandexUserData(BaseModel):
    id: int
    login: str
    name: str = Field(alias="real_name")
    default_email: str
    access_token: str
