from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.users.handlers import user_router, auth_router, account_router
from app.groups.handlers import group_router, group_member_router
from app.finance.handlers import cat_router, trans_router, plan_router, goal_router, debt_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081"],  # Allow your frontend domain
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

routers = [user_router, auth_router, account_router, group_router, group_member_router, cat_router, trans_router,
           plan_router, goal_router, debt_router]

for router in routers:
    app.include_router(router=router)
