import uuid
from typing import Dict

from asyncpg.pgproto.pgproto import UUID
from loguru import logger
from orjson import orjson

from app.config import configuration


def examina_logger_json_serializer(obj):
    """Create a custom serializer for UUID objects"""
    # Check if object is a UUID object
    if isinstance(obj, UUID):
        return str(obj)
    raise TypeError


def serialize_log_message(record: Dict):
    """
    This method is used by loguru to serialize the log message.

    :param record:
    :return:
    """
    timestamp = record["time"]
    timestamp = timestamp.strftime("%Y-%m-%dT%H:%M:%S.{:03d}Z").format(timestamp.microsecond // 1000)

    serializable = {
        # Base fields
        "log_uuid": str(uuid.uuid4()),
        "timestamp": timestamp,
        "status": record["level"].name,
        "name": record["name"],
        "message": record["message"],
        # Extra
        **record["extra"],
    }

    record["extra"]["serialized"] = orjson.dumps(serializable, default=examina_logger_json_serializer).decode("utf-8")
    return "{extra[serialized]}\n"


# Setup logger
logger.remove()
logger.configure()


# Creating file name
LOG_FILE_NAME = f"examina_api.log"

logger.add(
    sink=f"{configuration.AUDIT_LOG_LOCATION}/{LOG_FILE_NAME}",
    rotation="6 days",
    retention=5,
    serialize=False,
    format=serialize_log_message,
)
