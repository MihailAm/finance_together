from pathlib import Path

from pydantic.v1 import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_DRIVER: str

    PRIVATE_KEY_PATH: Path
    PUBLIC_KEY_PATH: Path
    JWT_ENCODE_ALGORITHM: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_SECRET_KEY: str
    GOOGLE_REDIRECT_URI: str
    GOOGLE_TOKEN_URL: str

    YANDEX_CLIENT_ID: str
    YANDEX_SECRET_KEY: str
    YANDEX_REDIRECT_URI: str
    YANDEX_TOKEN_URL: str

    model_config = ConfigDict(env_file=".local.env")

    @property
    def db_url(self):
        return f'{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    @property
    def google_redirect_url(self) -> str:
        return f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={self.GOOGLE_CLIENT_ID}&redirect_uri={self.GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&access_type=offline"

    @property
    def yandex_redirect_url(self) -> str:
        return f"https://oauth.yandex.ru/authorize?response_type=code&client_id={self.YANDEX_CLIENT_ID}&redirect_uri={self.YANDEX_REDIRECT_URI}"

