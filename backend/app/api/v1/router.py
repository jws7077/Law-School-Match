from fastapi import APIRouter

from app.api.v1.endpoints import health, match, schools

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(schools.router, prefix="/schools", tags=["schools"])
api_router.include_router(match.router, prefix="/matches", tags=["matches"])
