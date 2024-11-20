from passlib.context import CryptContext


class AuthService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Хэширует пароль для сохранения в базе данных.
        """
        return AuthService.pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Проверяет, соответствует ли введённый пароль хэшированному значению.
        """
        return AuthService.pwd_context.verify(plain_password, hashed_password)
