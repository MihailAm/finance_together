from contextlib import asynccontextmanager

from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi.middleware.cors import CORSMiddleware

from app.cron.goal import CronJobGoal
from app.cron.planned_expenses import CronJobPlannedExpenses
from app.dependecy import get_cron_job_goal, get_cron_job_planned_expenses

from app.users.handlers import user_router, auth_router, account_router
from app.groups.handlers import group_router, group_member_router
from app.finance.handlers import cat_router, trans_router, plan_router, goal_router, debt_router, goal_contrib_router


scheduler = AsyncIOScheduler()


async def run_auto_goal_payments(cron_job_goal: CronJobGoal):
    await cron_job_goal.process_auto_payments()

async def run_auto_planned_expenses(cron_job_planned_expenses: CronJobPlannedExpenses):
    await cron_job_planned_expenses.process_auto_payments()

@asynccontextmanager
async def lifespan(_: FastAPI):

    cron_job_goal = await get_cron_job_goal()
    cron_job_planned_expenses = await get_cron_job_planned_expenses()

    scheduler.add_job(run_auto_goal_payments, "interval", minutes=10, args=[cron_job_goal])
    scheduler.add_job(run_auto_planned_expenses, "interval", minutes=3, args=[cron_job_planned_expenses])

    print("⏳ Запуск планировщика задач...")
    scheduler.start()
    yield
    print("🛑 Остановка планировщика задач...")
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081"],  # Allow your frontend domain
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

routers = [user_router, auth_router, account_router, group_router, group_member_router, cat_router, trans_router,
           plan_router, goal_router, debt_router, goal_contrib_router]

for router in routers:
    app.include_router(router=router)
