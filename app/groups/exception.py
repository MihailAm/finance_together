class UserNotFoundInGroup(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class GroupNotFound(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AccessDenied(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
