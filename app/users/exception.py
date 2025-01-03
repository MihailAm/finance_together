class UserNotFoundException(Exception):
    detail = "User not found"


class UserNotCorrectPasswordException(Exception):
    detail = "User not correct password"


class TokenExpired(Exception):
    detail = "Token has expired"


class TokenNotCorrect(Exception):
    detail = "Token is not correct"


class JWTError(Exception):
    detail = "Token is not decoded"

class PasswordValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class TokenNotCorrectType(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AccountNotFound(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class GroupAccountConflictException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

class AccountAccessError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)