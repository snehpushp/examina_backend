import json
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, root_validator

from app.enums import CalculatorTypeEnum, PapersStatusEnum

# DATABASE SCHEMAS


class ExamsCreateDatabaseSchema(BaseModel):
    name: str
    description: Optional[str]


class ExamsUpdateDatabaseSchema(BaseModel):
    is_active: bool


class PapersCreateDatabaseSchema(BaseModel):
    exam_id: UUID
    name: str
    year: Optional[int] = Field(default=datetime.now().year)
    paper_set: Optional[str]
    status: PapersStatusEnum = Field(default=PapersStatusEnum.DRAFT)
    template_id: UUID
    language_id: UUID


class PapersUpdateDatabaseSchema(BaseModel):
    name: Optional[str]
    year: Optional[int]
    paper_set: Optional[str]
    template_id: Optional[UUID]
    language_id: Optional[UUID]


class ExamPatternSettingsSchema(BaseModel):
    total_time: int
    is_calculator_allowed: bool = Field(default=False)
    calculator_type: Optional[CalculatorTypeEnum] = Field(default=CalculatorTypeEnum.NORMAL)

    @root_validator
    def validate_calculator_type(cls, values):
        if not values.get("is_calculator_allowed"):
            values["calculator_type"] = None
        return values


class TemplatesCreateDatabaseSchema(BaseModel):
    name: str
    settings: dict
    instructions: Optional[str]

    @root_validator
    def validate_settings(cls, values):
        # Validate settings with ExamPatternSettingsSchema and order the keys
        settings = ExamPatternSettingsSchema(**values["settings"]).dict()
        if settings.get("calculator_type"):
            settings["calculator_type"] = settings["calculator_type"].value
        values["settings"] = json.loads(json.dumps(settings, sort_keys=True))

        # Convert instructions to title case, remove extra spaces
        values["instructions"] = values["instructions"].strip().title()

        return values


class TemplatesUpdateDatabaseSchema(BaseModel):
    pass


class SectionsCreateDatabaseSchema(BaseModel):
    name: str
    paper_id: UUID
    section_time: int
    order: int


class SectionsUpdateDatabaseSchema(BaseModel):
    name: Optional[str]
    section_time: Optional[int]


class SubSectionsCreateDatabaseSchema(BaseModel):
    name: str
    section_id: UUID
    order: int


class SubSectionsUpdateDatabaseSchema(BaseModel):
    name: Optional[str]


class SubSectionQuestionsCreateDatabaseSchema(BaseModel):
    sub_section_id: UUID
    question_id: UUID
    positive_marks: float
    negative_marks: float = Field(default=0.0)
    order: int


class SubSectionQuestionsUpdateDatabaseSchema(BaseModel):
    positive_marks: Optional[float]
    negative_marks: Optional[float]
