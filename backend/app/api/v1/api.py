from fastapi import APIRouter
from app.api.v1.endpoints import users, auth, schedule_templates, driver_preferences, schedule_generation, swap_requests, admin, student, statistics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(schedule_templates.router, prefix="/schedule-templates", tags=["schedule-templates"])
api_router.include_router(driver_preferences.router, prefix="/parent", tags=["parent-preferences"])
api_router.include_router(schedule_generation.router, prefix="/admin", tags=["admin-scheduling"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(swap_requests.router, prefix="/swap-requests", tags=["swap-requests"])
api_router.include_router(student.router, prefix="/student", tags=["student"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["statistics"])