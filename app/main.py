from fastapi import FastAPI

from app.users.handlers import user_router, auth_router, account_router
from app.groups.handlers import group_router, group_member_router
from app.finance.handlers import cat_router, trans_router, plan_router, goal_router

app = FastAPI()

routers = [user_router, auth_router, account_router, group_router, group_member_router, cat_router, trans_router,
           plan_router, goal_router]

for router in routers:
    app.include_router(router=router)
