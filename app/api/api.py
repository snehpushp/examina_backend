from fastapi import APIRouter

from app.api.v1 import api_v1_router

api_routers = APIRouter()
api_routers.include_router(api_v1_router)
