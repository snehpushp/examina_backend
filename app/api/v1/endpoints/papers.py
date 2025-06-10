from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status as http_status

from app.api.v1.dependencies import get_papers_service, get_sections_service, get_sub_sections_service
from app.api.v1.routers import ExaminaRouteWrapper
from app.core.schemas.exams import SectionsUpdateDatabaseSchema, SubSectionsUpdateDatabaseSchema
from app.core.services.exams import PapersService, SectionsService, SubSectionsService
from app.enums import PapersStatusEnum
from app.schemas import CBTPaperBaseSchema, CBTQuestionUpdateSchema, CBTResponseSchema

papers_router = APIRouter(prefix="/paper", tags=["Paper"], route_class=ExaminaRouteWrapper)
sections_router = APIRouter(prefix="/sections", tags=["Sections"], route_class=ExaminaRouteWrapper)
sub_sections_router = APIRouter(prefix="/sub_sections", tags=["Sub Sections"], route_class=ExaminaRouteWrapper)

# FETCH API


@papers_router.get(path="/{paper_id}", status_code=http_status.HTTP_200_OK, response_model=CBTResponseSchema)
async def get_paper_content(
    paper_id: UUID,
    papers_service: PapersService = Depends(get_papers_service),
):
    """Get content for CBT environment for a particular paper given its UUID"""
    cbt_paper_instance = await papers_service.get_for_cbt(paper_id)

    return cbt_paper_instance


@papers_router.get(path="/{paper_id}/solution", status_code=http_status.HTTP_200_OK)
async def get_paper_solution(
    paper_id: UUID,
    papers_service: PapersService = Depends(get_papers_service),
):
    """Get solution for a particular paper given its UUID"""
    solutions = await papers_service.get_solution(paper_id)

    return solutions


# DELETE API


@papers_router.delete(path="/{paper_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_paper(
    paper_id: UUID,
    papers_service: PapersService = Depends(get_papers_service),
):
    """Delete a paper from the database"""
    await papers_service.delete(paper_id)

    return None


# UPDATE API


@papers_router.patch(path="/{paper_id}/status", status_code=http_status.HTTP_200_OK)
async def update_status(
    paper_id: UUID,
    status: PapersStatusEnum,
    papers_service: PapersService = Depends(get_papers_service),
):
    """Update the status of the paper - PUBLISHED/ ARCHIVED"""
    paper_instance = await papers_service.update_status(paper_id, status)

    return paper_instance


@papers_router.patch(path="/{paper_id}", status_code=http_status.HTTP_200_OK)
async def update_paper(
    paper_id: UUID,
    paper_data: CBTPaperBaseSchema,
    papers_service: PapersService = Depends(get_papers_service),
):
    """Update paper details"""
    paper_instance = await papers_service.update_paper(paper_id, paper_data)

    return paper_instance


@sections_router.patch(path="/{section_id}", status_code=http_status.HTTP_200_OK)
async def update_section(
    section_id: UUID,
    section_data: SectionsUpdateDatabaseSchema,
    sections_service: SectionsService = Depends(get_sections_service),
):
    """Update section details"""
    section_instance = await sections_service.update(section_id, section_data)

    return section_instance


@sub_sections_router.patch(path="/{sub_section_id}", status_code=http_status.HTTP_200_OK)
async def update_sub_section(
    sub_section_id: UUID,
    sub_section_data: SubSectionsUpdateDatabaseSchema,
    sub_sections_service: SubSectionsService = Depends(get_sub_sections_service),
):
    """Update sub-section details"""
    sub_section_instance = await sub_sections_service.update(sub_section_id, sub_section_data)

    return sub_section_instance


@sub_sections_router.patch(path="/{sub_section_id}/{question_id}", status_code=http_status.HTTP_200_OK)
async def update_sub_section_question(
    sub_section_id: UUID,
    question_id: UUID,
    question_data: CBTQuestionUpdateSchema,
    sub_sections_service: SubSectionsService = Depends(get_sub_sections_service),
):
    """Update sub-section question"""
    sub_section_instance = await sub_sections_service.update_question(sub_section_id, question_id, question_data)

    return sub_section_instance
