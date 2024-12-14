import base64
import logging
import re
from dataclasses import dataclass

import bcrypt

from app.users.exception import PasswordValidationError
from app.users.repository import UserRepository
from app.users.schema import UserLoginSchema, UserCreateSchema
from app.users.service import AuthService

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@dataclass
class UserService:
    user_repository: UserRepository
    auth_service: AuthService

    async def create_user(self, name: str, surname: str, email: str, password: str) -> UserLoginSchema:
        self.validate_password(password)

        create_user_data = UserCreateSchema(
            name=name,
            surname=surname,
            email=email,
            password=self.hash_password(password)
        )
        user = await self.user_repository.create_user(create_user_data)
        payload = {
            'sub': user.id,
            'email': user.email,
        }
        access_token = self.auth_service.generate_access_token(payload=payload)
        return UserLoginSchema(user_id=user.id, access_token=access_token)



    @staticmethod
    def hash_password(password: str) -> str:
        logger.debug(f"Hashing password: {password}")
        salt = bcrypt.gensalt()
        pwd_bytes: bytes = password.encode()
        logger.debug(f"Encoded password (bytes): {pwd_bytes}")
        hashed_password: bytes = bcrypt.hashpw(pwd_bytes, salt)
        logger.debug(f"Hashed password (bytes): {hashed_password}")
        return base64.b64encode(hashed_password).decode()

    @staticmethod
    def validate_password(password: str) -> None:
        if len(password) < 6:
            raise PasswordValidationError("The password must contain at least 6 characters.")
        if not re.search(r'[A-Z]', password):
            raise PasswordValidationError("The password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            raise PasswordValidationError("The password must contain at least one lowercase letter.")
        if not re.search(r'[0-9]', password):
            raise PasswordValidationError("The password must contain at least one number.")