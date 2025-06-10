from typing import Any, List, Optional, Type
from uuid import UUID

from pydantic import BaseModel, Field, root_validator

from app.core.schemas.base import ORMBaseSchema
from app.enums import ContentTypeEnum, LanguageEnum, QuestionTypeEnum

# DATABASE SCHEMAS


class QuestionsCreateSchema(BaseModel):
    question: str
    explanation: Optional[str]
    question_type: QuestionTypeEnum
    subject_id: UUID
    content_type: ContentTypeEnum
    passage_id: Optional[UUID]
    language_id: UUID
    knowledge_level: int
    difficulty: int = Field(default=500)
    source: Optional[str]


class QuestionsUpdateSchema(ORMBaseSchema):
    question: Optional[str]
    explanation: Optional[str]
    knowledge_level: Optional[int]
    difficulty: Optional[int]
    question_type: Optional[QuestionTypeEnum]
    subject_id: Optional[UUID]
    content_type: Optional[ContentTypeEnum]
    passage_id: Optional[UUID]
    language_id: Optional[UUID]
    source: Optional[str]


class SubjectsCreateSchema(BaseModel):
    name: str


class SubjectsUpdateSchema(BaseModel):
    pass


class PassagesCreateUpdateSchema(BaseModel):
    passage_text: str

    @root_validator
    def validate_passage_text(cls, values):
        # Strip the passage text
        values["passage_text"] = values["passage_text"].strip()
        return values


class TagsCreateUpdateSchema(BaseModel):
    tag_name: str
    subject_id: UUID


class QuestionTagsCreateUpdateSchema(BaseModel):
    question_id: UUID
    tag_id: UUID


class OptionsCreateSchema(BaseModel):
    option: str
    question_id: UUID
    option_order: int
    is_correct_option: bool


class OptionsUpdateSchema(BaseModel):
    option: Optional[str]
    is_correct_option: Optional[bool]


class RangeAnswerCreateSchema(BaseModel):
    question_id: UUID
    start: float
    end: float


class RangeAnswerUpdateSchema(BaseModel):
    start: Optional[float]
    end: Optional[float]


class LanguageCreateUpdateSchema(BaseModel):
    name: LanguageEnum


# AUXILIARY SCHEMAS


class OptionsUploadSchema(BaseModel):
    option: str
    option_order: Optional[int]
    is_correct_option: bool


class RangeAnswerUploadSchema(BaseModel):
    start: float
    end: float


class QuestionsUploadSchema(BaseModel):
    # Model values
    question: str
    explanation: Optional[str]
    question_type: QuestionTypeEnum
    content_type: ContentTypeEnum = Field(default=ContentTypeEnum.NORMAL)
    subject: str
    language: Optional[LanguageEnum]
    knowledge_level: int = Field(default=12)
    difficulty: Optional[int]
    source: Optional[str]
    passage: Optional[str]

    # Additional values
    tags: Optional[List[str]] = Field(default=[])
    answer: Optional[RangeAnswerUploadSchema]
    options: Optional[List[OptionsUploadSchema]]

    @classmethod
    def parse_obj(cls: Type["Model"], obj: Any) -> "Model":
        if obj.get("options"):
            options = []
            for idx, option in enumerate(obj["options"]):
                option["option_order"] = idx + 1
                options.append(OptionsUploadSchema.parse_obj(option))
            obj["options"] = options
        elif not obj.get("answer"):
            raise ValueError("Either options or range answer should be provided")
        return super().parse_obj(obj)

    @root_validator  # Using root validator as knowledge_level have a default value
    def populate_values(cls, values):
        # If difficulty is not provided, set it to 100 * knowledge_level
        if not values.get("difficulty"):
            values["difficulty"] = 100 * values["knowledge_level"]

        # Populating content_type
        if values.get("passage"):
            values["content_type"] = ContentTypeEnum.PASSAGE
        else:
            values["content_type"] = ContentTypeEnum.NORMAL
        return values
