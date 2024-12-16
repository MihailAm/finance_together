from pydantic import BaseModel, EmailStr, Field


class AuthJwtSchema(BaseModel):
    email: EmailStr
    password: str | bytes


class GoogleUserData(BaseModel):
    id: int
    name: str = Field(alias="given_name")
    surname: str = Field(alias="family_name")
    email: str


class YandexUserData(BaseModel):
    id: int
    name: str = Field(alias="first_name")
    surname: str = Field(alias="last_name")
    email: str = Field(alias="default_email")
