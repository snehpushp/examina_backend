from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status as http_status

from app.api.v1.dependencies import get_exams_service, get_papers_service
from app.api.v1.routers import ExaminaRouteWrapper
from app.core.schemas.exams import ExamsCreateDatabaseSchema
from app.core.services.exams import ExamsService, PapersService
from app.enums import PapersStatusEnum
from app.schemas import CBTRequestSchema, ExamsResponseSchema, PapersResponseSchema

exams_router = APIRouter(prefix="/exams", tags=["Exams"], route_class=ExaminaRouteWrapper)

# FETCH API


@exams_router.get(path="/", status_code=http_status.HTTP_200_OK, response_model=List[ExamsResponseSchema])
async def get_exams(
    include_inactive: bool = False,
    exams_service: ExamsService = Depends(get_exams_service),
):
    """Fetch all the exams that are available in the database"""
    exam_instances = await exams_service.get_exams(include_inactive)

    return exam_instances


@exams_router.get(
    path="/{exam_id}/papers", status_code=http_status.HTTP_200_OK, response_model=List[PapersResponseSchema]
)
async def get_papers_by_exam_id(
    exam_id: UUID,
    paper_status: PapersStatusEnum,
    exams_service: ExamsService = Depends(get_exams_service),
):
    """Fetch all the papers for a particular exam"""
    paper_instances = await exams_service.get_papers(exam_id=exam_id, paper_status=paper_status)

    return paper_instances


# CREATE API


@exams_router.post(path="/", status_code=http_status.HTTP_201_CREATED)
async def create_exams(
    request_body: List[ExamsCreateDatabaseSchema],
    exams_service: ExamsService = Depends(get_exams_service),
):
    """Create a bunch of new exam - SSC, JEE Mains, and so on"""
    # This will mainly be used to add all initial exams to the database in one go
    exam_instance = await exams_service.create_bulk(request_body)

    return exam_instance


@exams_router.post(path="/{exam_id}/paper", status_code=http_status.HTTP_201_CREATED)
async def create_paper(
    exam_id: UUID,
    request_body: CBTRequestSchema,
    papers_service: PapersService = Depends(get_papers_service),
):
    """Create a new paper for an exam - JEE Mains 2021, SSC CGL 2020, etc."""
    paper_instance = await papers_service.create_paper(exam_id, request_body)

    return paper_instance


# DELETE API


@exams_router.delete(path="/{exam_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_exam(
    exam_id: UUID,
    exams_service: ExamsService = Depends(get_exams_service),
):
    """Delete an exam from the database"""
    await exams_service.delete(exam_id)

    return None


# UPDATE API


@exams_router.patch(path="/{exam_id}/active", status_code=http_status.HTTP_200_OK)
async def update_exam_active_status(
    exam_id: UUID,
    is_active: bool,
    exams_service: ExamsService = Depends(get_exams_service),
):
    """Update the active status of an exam"""
    exam_instance = await exams_service.update_active_status(exam_id, is_active)

    return exam_instance
