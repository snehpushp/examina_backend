import uuid

from sqlalchemy import Boolean, Column, MetaData, func
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import declarative_base

from app.config import configuration

# Add specific database schema
metadata = MetaData(schema=configuration.POSTGRES_DATABASE_SCHEMA)


class BaseMixin(object):
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


Base = declarative_base(cls=BaseMixin, metadata=metadata)


# Soft delete
class SoftDeleteBaseMixin(BaseMixin):
    is_deleted = Column(Boolean, default=False)


SoftDeleteBase = declarative_base(cls=SoftDeleteBaseMixin, metadata=metadata)


# Base class for view
BaseForView = declarative_base(metadata=metadata)
