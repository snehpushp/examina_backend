from sqlalchemy import UUID, Boolean, Column
from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Text, UniqueConstraint

from app.config import configuration
from app.core.models.base import Base, SoftDeleteBase
from app.enums import ContentTypeEnum, LanguageEnum, QuestionTypeEnum


class QuestionsModel(SoftDeleteBase):
    __tablename__ = "questions"

    question = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    question_type = Column(
        SqlAlchemyEnum(QuestionTypeEnum, schema=configuration.POSTGRES_DATABASE_SCHEMA), nullable=False
    )
    content_type = Column(
        SqlAlchemyEnum(ContentTypeEnum, schema=configuration.POSTGRES_DATABASE_SCHEMA), nullable=False
    )
    passage_id = Column(UUID(as_uuid=True), ForeignKey("passages.uuid"), nullable=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.uuid"), nullable=False)
    # Assuming that class number (1-12 to 13+) represents the knowledge required.
    # Interlinked with the subject and not exam
    knowledge_level = Column(Integer, nullable=True)
    difficulty = Column(Integer, nullable=False, default=500)
    source = Column(String(128), nullable=True)
    language_id = Column(UUID(as_uuid=True), ForeignKey("language.uuid"), nullable=False)


class SubjectsModel(SoftDeleteBase):
    __tablename__ = "subjects"

    name = Column(String(128), nullable=False, unique=True)


class PassagesModel(SoftDeleteBase):
    __tablename__ = "passages"

    passage_text = Column(Text, nullable=False)


class TagsModel(Base):
    __tablename__ = "tags"

    tag_name = Column(String(128), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.uuid"), nullable=False)


class QuestionTagsModel(Base):
    __tablename__ = "question_tags"

    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.uuid"), nullable=False)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.uuid"), nullable=False)


class OptionsModel(SoftDeleteBase):
    __tablename__ = "options"

    option = Column(Text, nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.uuid"), nullable=False)
    option_order = Column(Integer, nullable=False)
    is_correct_option = Column(Boolean, nullable=False)

    __table_args__ = (UniqueConstraint("question_id", "option_order", name="unique_option_order"),)


class RangeAnswersModel(SoftDeleteBase):  # In case of value problems
    __tablename__ = "range_answers"

    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.uuid"), nullable=False)
    start = Column(Float, nullable=False)
    end = Column(Float, nullable=False)


class LanguageModel(Base):
    __tablename__ = "language"

    name = Column(SqlAlchemyEnum(LanguageEnum, schema=configuration.POSTGRES_DATABASE_SCHEMA), nullable=False)
