import base64
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

import jwt
import bcrypt
from jwt import DecodeError

from app.settings import Settings
from app.users.exception import TokenNotCorrect, TokenExpired, UserNotFoundException, UserNotCorrectPasswordException
from app.users.repository import UserRepository
from app.users.schema import UserLoginSchema

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class AuthService:
    setting: Settings
    user_repository: UserRepository

    async def login(self, email: str, password: str) -> UserLoginSchema:
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise UserNotFoundException
        if not self.validate_password(password=password, hashed_password=user.password):
            raise UserNotCorrectPasswordException

        payload = {
            'sub': user.id,
            'email': user.email,
        }

        access_token = self.generate_access_token(payload)
        return UserLoginSchema(user_id=user.id, access_token=access_token)

    def generate_access_token(self, payload) -> str:
        to_encode = payload.copy()
        expire = datetime.now() + timedelta(minutes=5)

        to_encode.update(
            exp=expire,
        )

        token = jwt.encode(
            to_encode,
            key=self.setting.PRIVATE_KEY_PATH.read_text(),
            algorithm=self.setting.JWT_ENCODE_ALGORITHM
        )
        return token

    @staticmethod
    def validate_password(password: str, hashed_password: str) -> bool:
        logger.debug(f"Password: {password}")
        logger.debug(f"Hashed password from DB (Base64): {hashed_password}")

        try:
            stored_hash = base64.b64decode(hashed_password.encode())
        except Exception as e:
            logger.error(f"Failed to decode Base64: {e}")
            return False

        logger.debug(f"Decoded stored hash (bcrypt format): {stored_hash}")

        is_valid = bcrypt.checkpw(password.encode(), stored_hash)
        logger.debug(f"Password validation result: {is_valid}")
        return is_valid

    def get_user_id_from_access_token(self, access_token: str | bytes):
        try:
            decoded = jwt.decode(
                access_token,
                key=self.setting.PUBLIC_KEY_PATH.read_text(),
                algorithms=[self.setting.JWT_ENCODE_ALGORITHM]
            )
        except DecodeError:
            raise TokenNotCorrect

        if decoded['exp'] < datetime.now().timestamp():
            raise TokenExpired

        return decoded['user_id']
