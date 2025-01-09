class CategoryNotFound(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class TransactionNotFound(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AccessDeniedTransaction(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
