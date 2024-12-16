from fastapi import FastAPI

from app.users.handlers import user_router, auth_router

app = FastAPI()

routers = [user_router, auth_router]

for router in routers:
    app.include_router(router=router)
