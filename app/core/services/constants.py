from typing import TypeVar

from pydantic import BaseModel

from app.core.models.base import Base, SoftDeleteBase

# Common schema types
ModelType = TypeVar("ModelType", bound=Base)
SoftDeleteModelType = TypeVar("SoftDeleteModelType", bound=SoftDeleteBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
