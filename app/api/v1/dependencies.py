from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db.session import get_async_session
from app.core.services.exams import ExamsService, PapersService, SectionsService, SubSectionsService
from app.core.services.questions import QuestionsService


def get_questions_service(session: Session = Depends(get_async_session)):
    """Create questions service class instance"""
    yield QuestionsService(session=session)


def get_exams_service(session: Session = Depends(get_async_session)):
    """Create exams service class instance"""
    yield ExamsService(session=session)


def get_papers_service(session: Session = Depends(get_async_session)):
    """Create papers service class instance"""
    yield PapersService(session=session)


def get_sections_service(session: Session = Depends(get_async_session)):
    """Create sections service class instance"""
    yield SectionsService(session=session)


def get_sub_sections_service(session: Session = Depends(get_async_session)):
    """Create subsections service class instance"""
    yield SubSectionsService(session=session)
