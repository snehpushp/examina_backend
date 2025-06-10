from sqlalchemy import JSON, UUID, Boolean, Column
from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Text, UniqueConstraint

from app.config import configuration
from app.core.models.base import Base, SoftDeleteBase
from app.enums import PapersStatusEnum


class ExamsModel(SoftDeleteBase):  # This model stores exams list - JEE Mains, SSC, etc.
    __tablename__ = "exams"

    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)  # Information about exam, which can be shown before the exam starts
    is_active = Column(Boolean, nullable=False, default=False)


class PapersModel(SoftDeleteBase):  # This model stores the papers for the exams - JEE Mains 2021, SSC CGL 2020, etc.
    __tablename__ = "papers"

    exam_id = Column(UUID(as_uuid=True), ForeignKey("exams.uuid"), nullable=False)
    name = Column(String(128), nullable=False)
    year = Column(Integer, nullable=False)  # This will have default value as current year
    paper_set = Column(String(128), nullable=True)  # A, B, C, etc.
    status = Column(
        SqlAlchemyEnum(PapersStatusEnum, schema=configuration.POSTGRES_DATABASE_SCHEMA),
        nullable=False,
        default=PapersStatusEnum.DRAFT,
    )
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.uuid"), nullable=False)
    language_id = Column(UUID(as_uuid=True), ForeignKey("language.uuid"), nullable=False)

    # Unique constraint for year, name, and paper_set
    __table_args__ = (
        UniqueConstraint(
            "exam_id", "language_id", "year", "name", "paper_set", "is_deleted", name="unique_exam_paper_set"
        ),
    )


class TemplatesModel(Base):  # This stores the settings/ exam pattern for the papers
    __tablename__ = "templates"

    name = Column(String(128), nullable=False)
    settings = Column(JSON, nullable=False)  # This will store JSON data for the exam pattern
    instructions = Column(Text, nullable=True)  # This can be used to store the instructions for the exam "format"


class SectionsModel(Base):  # For each paper, there can be multiple sections - Physics, Chemistry, etc.
    __tablename__ = "sections"

    name = Column(String(128), nullable=False)
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.uuid"), nullable=False)
    section_time = Column(Integer, nullable=False)  # Time in minutes
    order = Column(Integer, nullable=False)


class SubSectionsModel(Base):  # For each section, there can be multiple subsections - Example CAT exam
    __tablename__ = "sub_sections"

    name = Column(String(128), nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.uuid"), nullable=False)
    order = Column(Integer, nullable=False)


class SubSectionQuestionsModel(Base):  # We link questions with subsections here
    __tablename__ = "sub_section_questions"

    sub_section_id = Column(UUID(as_uuid=True), ForeignKey("sub_sections.uuid"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.uuid"), nullable=False)
    positive_marks = Column(Float, nullable=False)
    negative_marks = Column(Float, nullable=False, default=0.0)
    order = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("sub_section_id", "question_id", name="unique_sub_section_question"),
        UniqueConstraint("sub_section_id", "order", name="unique_sub_section_order"),
    )
