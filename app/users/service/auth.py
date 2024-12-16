import base64
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

import jwt
import bcrypt
from jwt import InvalidTokenError

from app.settings import Settings
from app.users.client import GoogleClient
from app.users.client.yandex import YandexClient
from app.users.exception import TokenNotCorrect, TokenExpired, UserNotFoundException, UserNotCorrectPasswordException, \
    TokenNotCorrectType, PasswordValidationError

from app.users.repository import UserRepository
from app.users.schema import UserLoginSchema, UserCreateSchema, YandexUserData, GoogleUserData

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class AuthService:
    setting: Settings
    user_repository: UserRepository
    google_client: GoogleClient
    yandex_client: YandexClient

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
        expire = now + timedelta(minutes=15)
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

    def get_google_redirect_url(self):
        return self.setting.google_redirect_url

    def get_yandex_redirect_url(self):
        return self.setting.yandex_redirect_url

    async def authenticate_oauth(self, user_data: GoogleUserData | YandexUserData) -> UserLoginSchema:
        user = await self.user_repository.get_user_by_email(email=user_data.email)
        if user:
            access_token = await self.generate_access_token(user_id=user.id)
            refresh_token = self.generate_refresh_token(user=user)
            return UserLoginSchema(access_token=access_token,
                                   refresh_token=refresh_token)

        create_user_data = UserCreateSchema(
            name=user_data.name,
            surname=user_data.surname,
            email=user_data.email
        )

        created_user = await self.user_repository.create_user(user=create_user_data)

        access_token = await self.generate_access_token(user_id=created_user.id)
        refresh_token = self.generate_refresh_token(user=created_user)
        return UserLoginSchema(access_token=access_token,
                               refresh_token=refresh_token)

    async def google_auth(self, code: str):
        user_data = await self.google_client.get_user_info(code=code)

        return await self.authenticate_oauth(user_data=user_data)

    async def yandex_auth(self, code: str):
        user_data = await self.yandex_client.get_user_info(code=code)

        return await self.authenticate_oauth(user_data=user_data)
