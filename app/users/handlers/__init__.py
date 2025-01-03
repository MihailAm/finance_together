from app.users.handlers.user import router as user_router
from app.users.handlers.auth import router as auth_router
from app.users.handlers.account import router as account_router

__all__ = ["user_router",
           "auth_router",
           "account_router"]
