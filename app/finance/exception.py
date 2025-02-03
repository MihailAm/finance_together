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


class PlannedExpensesNotFound(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class GoalNotFound(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AccessDeniedGoal(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class DebtNotFound(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AccessDeniedDebt(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class GoalsNotFound(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
