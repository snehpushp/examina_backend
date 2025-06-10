from typing import Any, Dict, Generic, Optional, Type, Union
from uuid import UUID

from fastapi import HTTPException
from loguru import logger
from starlette import status

from app.core.services.constants import ModelType

# This logger will be used to print logs before raising an exception


class ExaminaBaseException(HTTPException):
    """Base Exception class for all custom exceptions in this project."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status_code,
            detail=message,
            headers=headers,
        )


class UUIDNotFoundException(ExaminaBaseException, Generic[ModelType]):
    """Custom exception class for handling cases where a record is not found in database"""

    def __init__(
        self,
        model: Type[ModelType],
        uuid: Optional[Union[UUID, str]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        error_message = (
            f"Unable to find the {model.__tablename__} with uuid: {uuid}"
            if uuid
            else f"{model.__tablename__} uuid not found"
        )

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=error_message,
            headers=headers,
        )


class NoFilterFoundException(ExaminaBaseException):
    """Custom exception class for handling cases where no filter/condition passed to update bulk records"""

    def __init__(self, model: Type[ModelType]) -> None:
        error_message = f"You are trying to update all records at once in {model.__tablename__} which is not allowed."
        super().__init__(error_message)


class DataLogicException(ExaminaBaseException):
    """Custom exception class for handling cases where data logic is not followed"""

    def __init__(self, error_message: str, headers: Optional[Dict[str, Any]] = None, *args, **kwargs) -> None:
        message = f"Logic Error: {error_message}"

        # Update the error message in the logs by adding args, kwargs to it
        if args:
            error_message += f" {args}"
        if kwargs:
            error_message += f" {kwargs}"
        logger.error(error_message)

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            headers=headers,
        )
