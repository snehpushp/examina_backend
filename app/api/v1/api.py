from fastapi import APIRouter

from app.api.v1.endpoints import exams_router
from app.api.v1.endpoints.papers import papers_router, sections_router, sub_sections_router
from app.api.v1.endpoints.questions import questions_router

api_v1_router = APIRouter(
    prefix="/v1",
)
api_v1_router.include_router(questions_router)
api_v1_router.include_router(exams_router)
api_v1_router.include_router(papers_router)
api_v1_router.include_router(sections_router)
api_v1_router.include_router(sub_sections_router)
