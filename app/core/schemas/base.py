from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ORMBaseSchema(BaseModel):
    class Config:
        orm_mode = True


class ExaminaBaseSchema(ORMBaseSchema):
    uuid: UUID
    created_at: datetime
    updated_at: datetime


class ExaminaSoftDeleteBaseSchema(ExaminaBaseSchema):
    is_deleted: bool
