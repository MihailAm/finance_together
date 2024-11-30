from pydantic import BaseModel, EmailStr


class AuthJwtSchema(BaseModel):
    email: EmailStr
    password: str | bytes