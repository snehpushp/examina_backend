from typing import List

from fastapi import APIRouter, Depends
from starlette import status as http_status

from app.api.v1.dependencies import get_questions_service
from app.api.v1.routers import ExaminaRouteWrapper
from app.core.schemas.questions import QuestionsUploadSchema
from app.core.services.questions import QuestionsService

questions_router = APIRouter(prefix="/questions", tags=["Questions"], route_class=ExaminaRouteWrapper)


@questions_router.post(path="/create", status_code=http_status.HTTP_201_CREATED)
async def create_questions(
    request_body: QuestionsUploadSchema,
    questions_service: QuestionsService = Depends(get_questions_service),
):
    """Upload questions to the database"""
    question_instance = await questions_service.create(request_body.dict())

    return question_instance


@questions_router.post(path="/bulk_create", status_code=http_status.HTTP_201_CREATED)
async def bulk_create_questions(
    request_body: List[QuestionsUploadSchema],
    questions_service: QuestionsService = Depends(get_questions_service),
):
    """Upload questions to the database"""
    question_instance = await questions_service.create_bulk([question.dict() for question in request_body])

    return question_instance
