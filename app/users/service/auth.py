import base64
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

import jwt
import bcrypt
from jwt import InvalidTokenError

from app.settings import Settings
from app.users.exception import TokenNotCorrect, TokenExpired, UserNotFoundException, UserNotCorrectPasswordException, \
    TokenNotCorrectType, PasswordValidationError
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

        access_token = await self.generate_access_token(user_id=user.id)
        refresh_token = self.generate_refresh_token(user=user)
        return UserLoginSchema(access_token=access_token,
                               refresh_token=refresh_token)

    def create_jwt(self, token_type: str, token_data: dict) -> str:
        jwt_payload = {self.setting.TOKEN_TYPE_FIELD: token_type}
        jwt_payload.update(token_data)
        token = jwt.encode(
            jwt_payload,
            key=self.setting.PRIVATE_KEY_PATH.read_text(),
            algorithm=self.setting.JWT_ENCODE_ALGORITHM
        )
        return token

    async def generate_access_token(self, user_id: int) -> str:
        user = await self.user_repository.get_user(user_id=user_id)
        now = datetime.now()
        expire = now + timedelta(days=5)
        to_encode = {
            'sub': user.email,
            'user_id': user.id,
            'iat': now.timestamp(),
            'exp': expire,
        }

        return self.create_jwt(token_type=self.setting.ACCESS_TOKEN_TYPE, token_data=to_encode)

    def generate_refresh_token(self, user):
        now = datetime.now()
        expire = now + timedelta(days=30)
        to_encode = {
            'user_id': user.id,
            'iat': now.timestamp(),
            'exp': expire
        }

        return self.create_jwt(token_type=self.setting.REFRESH_TOKEN_TYPE, token_data=to_encode)

    @staticmethod
    def validate_password(password: str, hashed_password: str) -> bool:
        try:
            stored_hash = base64.b64decode(hashed_password.encode())
        except PasswordValidationError as e:
            return False

        is_valid = bcrypt.checkpw(password.encode(), stored_hash)

        return is_valid

    def validate_token_type(self, payload: dict,
                            token_type: str) -> bool:
        current_token_type = payload.get(self.setting.TOKEN_TYPE_FIELD)
        if current_token_type == token_type:
            return True
        raise TokenNotCorrectType(message=f"Invalid token type {current_token_type} expected {token_type}")

    def get_user_id_from_token(self, token: str | bytes, expected_token_type: str) -> int:

        try:

            decoded = jwt.decode(
                jwt=token,
                key=self.setting.PUBLIC_KEY_PATH.read_text(),
                algorithms=[self.setting.JWT_ENCODE_ALGORITHM]
            )
        except InvalidTokenError:
            raise TokenNotCorrect

        self.validate_token_type(decoded, expected_token_type)

        if decoded['exp'] < datetime.now().timestamp():
            raise TokenExpired

        return decoded['user_id']

    def get_user_id_from_access_token(self, access_token: str | bytes) -> int:
        return self.get_user_id_from_token(access_token, self.setting.ACCESS_TOKEN_TYPE)

    def get_user_id_from_refresh_token(self, refresh_token: str | bytes) -> int:
        return self.get_user_id_from_token(refresh_token, self.setting.REFRESH_TOKEN_TYPE)
