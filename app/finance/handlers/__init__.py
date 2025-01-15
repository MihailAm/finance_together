from app.finance.handlers.category import router as cat_router
from app.finance.handlers.transaction import router as trans_router
from app.finance.handlers.planned_expenses import router as plan_router
from app.finance.handlers.goal import router as goal_router
from app.finance.handlers.debt import router as debt_router

__all__ = ["cat_router",
           "trans_router",
           "plan_router",
           "goal_router",
           "debt_router"]
