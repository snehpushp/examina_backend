from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, root_validator

from app.core.schemas.base import ORMBaseSchema
from app.core.schemas.exams import ExamPatternSettingsSchema
from app.core.schemas.questions import QuestionsUploadSchema
from app.enums import ContentTypeEnum, LanguageEnum, QuestionTypeEnum

# RESPONSE SCHEMAS


class ExamsResponseSchema(ORMBaseSchema):
    uuid: UUID
    name: str
    is_active: bool


class PapersResponseSchema(ORMBaseSchema):
    uuid: UUID
    name: str


# BASE SCHEMA


class CBTSettingsSchema(ExamPatternSettingsSchema):
    pass


class CBTPaperBaseSchema(BaseModel):
    name: str
    instructions: str
    year: int
    paper_set: str
    settings: CBTSettingsSchema
    language: LanguageEnum


# CBT RESPONSE SCHEMAS


class CBTOptionsResponseSchema(ORMBaseSchema):
    uuid: UUID
    option: str


class QuestionsResponseSchema(ORMBaseSchema):
    uuid: UUID
    question: str
    question_type: QuestionTypeEnum
    content_type: ContentTypeEnum
    passage: Optional[str]
    options: Optional[List[CBTOptionsResponseSchema]] = Field(default=[])

    @root_validator
    def validate_question_type(cls, values):
        if values.get("question_type") in [QuestionTypeEnum.MCQ.value, QuestionTypeEnum.MSQ.value]:
            if not values.get("options"):
                raise ValueError(
                    f"Options are required for multiple choice questions, for question {values.get('question')}"
                )
            elif len(values.get("options")) < 2:
                raise ValueError(f"Minimum 2 options are required, for question {values.get('question')}")
        return values


class CBTQuestionsResponseSchema(QuestionsResponseSchema):
    positive_marks: float
    negative_marks: float


class CBTSubSectionsResponseSchema(BaseModel):
    uuid: Optional[UUID]
    name: str

    questions: List[CBTQuestionsResponseSchema]


class CBTSectionsResponseSchema(BaseModel):
    uuid: Optional[UUID]
    name: str
    section_time: int
    sub_sections: List[CBTSubSectionsResponseSchema]


class CBTResponseSchema(CBTPaperBaseSchema):
    # Paper Details
    uuid: Optional[UUID]
    year: int = Field(default=datetime.now().year)
    paper_set: str = Field(default="A")

    # Sections
    sections: List[CBTSectionsResponseSchema]


# CBT REQUEST SCHEMAS


class CBTQuestionsRequestSchema(QuestionsUploadSchema):
    positive_marks: float
    negative_marks: float


class CBTSubSectionsRequestSchema(CBTSubSectionsResponseSchema):
    questions: List[CBTQuestionsRequestSchema]


class CBTSectionsRequestSchema(CBTSectionsResponseSchema):
    sub_sections: List[CBTSubSectionsRequestSchema]


class CBTSettingsRequestSchema(CBTSettingsSchema):
    pass


class CBTRequestSchema(CBTResponseSchema):
    settings: CBTSettingsRequestSchema
    sections: List[CBTSectionsRequestSchema]


# UPDATE SCHEMAS


class CBTQuestionUpdateSchema(BaseModel):
    # Model values
    question: Optional[str]
    explanation: Optional[str]
    # We are not providing question_type here as it'd also require options/answers to be updated
    content_type: Optional[ContentTypeEnum]
    subject: Optional[str]
    language: Optional[LanguageEnum]
    knowledge_level: Optional[int]
    difficulty: Optional[int]
    source: Optional[str]
    passage: Optional[str]

    # Additional values
    tags: Optional[List[str]]
    positive_marks: Optional[float]
    negative_marks: Optional[float]
