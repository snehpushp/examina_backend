from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, Union
from uuid import UUID

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from loguru import logger
from sqlalchemy import Executable, ScalarResult, desc, func, not_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.services.constants import CreateSchemaType, ModelType, SoftDeleteModelType, UpdateSchemaType
from app.enums import IOrderEnum
from app.logger import logger as audit_logger
from app.utils.exceptions.common_exceptions import NoFilterFoundException, UUIDNotFoundException


class ServiceInterface(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Common interface and dependencies that are shared by all CRUD classes that inherit from this.
    The subclass should implement the abstract methods defined in the base class and provide the
    necessary implementation details for managing the specific Model.
    """

    def __init__(
        self,
        model: Type[ModelType],
        session: AsyncSession,
        raised_http_exception_on_not_found: bool = True,
    ):
        self.model = model
        self.session = session
        self.raised_http_exception_on_not_found = raised_http_exception_on_not_found

    @abstractmethod
    async def get(self, uuid: Union[UUID, str]) -> Optional[ModelType]:
        """Get an instance of the model by uuid"""

    @abstractmethod
    async def get_by_uuids(self, list_uuids: List[Union[UUID, str]]) -> Optional[List[ModelType]]:
        """Get an instances of the model by list of uuid"""

    @abstractmethod
    async def get_count(self) -> int:
        """Get table record count"""

    @abstractmethod
    async def get_all(self) -> List[ModelType]:
        """Get all records from the table"""

    @abstractmethod
    async def create(self, instance: CreateSchemaType) -> ModelType:
        """Create a new instance of the model"""

    @abstractmethod
    async def create_bulk(self, instances: List[CreateSchemaType]) -> List[ModelType]:
        """Create the new instances of the model"""

    @abstractmethod
    async def update(
        self,
        current_instance: ModelType,
        updated_instance: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """Update an instance of the model"""

    @abstractmethod
    async def update_bulk(self, filters: List, updated_values: Union[UpdateSchemaType, Dict[str, Any]]):
        """
        Update multiple records using filter

        :param filters: List of filter/condition
        :param updated_values: Updated fields values
        :return:

        """

    @abstractmethod
    async def delete(self, uuid: Union[UUID, str]) -> ModelType:
        """Delete an instance of the model"""

    @abstractmethod
    async def filter(
        self, filters: List, entities: List = None, scalar_result: bool = False
    ) -> Optional[List[ModelType]]:
        """
        Fetch record by using filters

        :param filters: List of filter/condition
        :param entities: List of fields. Used to get specifics fields from database
        :param scalar_result: This allows user to fetch ScalerResult class object and
                allowing them to fetch data according to their needs
        :return:
        """

    @abstractmethod
    async def get_multi_paginated_ordered(
        self,
        entities: List = None,
        filters: List = None,
        params: Optional[Params] = Params(),
        order_by: Optional[str] = None,
        order: Optional[IOrderEnum] = IOrderEnum.asc,
    ) -> Page[ModelType]:
        """
        Fetch the items from database in pagination format

        :param entities: List of fields. Used to get specifics fields from database
        :param filters: List of filter/condition
        :param params: Used to paginate records
        :param order_by: Field name used to order fetched records
        :param order: To get records in ASC/DESC
        :return:
        """

    @staticmethod
    def get_model_instance_as_dict(instance: ModelType, columns: Optional[List] = None) -> Dict[str, Any]:
        """Convert model instance to dict"""
        # Get all columns if columns not passed
        if not columns:
            columns = instance.__table__.columns.keys()

        instance_dict = dict()
        instance_value_dict = instance.__dict__  # type: ignore
        for column in columns:
            value = instance_value_dict.get(column)
            instance_dict[column] = value
        return instance_dict


class BaseService(ServiceInterface, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Implemented base CRUD operations using SQLAlchemy"""

    def _get_records_query(self, uuids: List[Union[UUID, str]]) -> Executable:
        """Build statement to get the records"""
        return select(self.model).where(self.model.uuid.in_(uuids))

    async def get(self, uuid: UUID) -> Optional[ModelType]:
        """Get an instance of the model by uuid"""
        result = await self.session.execute(self._get_records_query(uuids=[uuid]))
        instance = result.scalar_one_or_none()

        # Raised error if instance is none and raised_exception_on_not_found is True
        if not instance and self.raised_http_exception_on_not_found:
            logger.warning(f"{self.model.__tablename__} with uuid {uuid} not found")
            raise UUIDNotFoundException(self.model, uuid=uuid)
        return instance

    async def get_by_uuids(self, uuids: List[Union[UUID, str]]) -> Optional[List[ModelType]]:
        """Get an instances of the model by list of uuid"""
        result = await self.session.execute(self._get_records_query(uuids=uuids))
        return result.scalars().all() or []

    async def get_count(self) -> int:
        """Get table record count"""
        result = await self.session.execute(select(func.count()).select_from(select(self.model).subquery()))
        return result.scalar_one()

    async def get_all(self) -> List[ModelType]:
        """Get all records from the table"""
        result = await self.session.execute(select(self.model))
        return result.scalars().all() or []

    async def create(self, instance: CreateSchemaType) -> ModelType:
        """Create a new instance of the model"""
        db_instance = self.model(**instance.dict())
        self.session.add(db_instance)
        await self.session.flush()

        # Log the audit and info logs
        message = f"Created new {self.model.__tablename__} record with uuid: {db_instance.uuid}"
        logger.info(message)
        audit_logger.info(
            message,
            previous_state={},
            current_state=self.get_model_instance_as_dict(db_instance),
            reference_uuid=db_instance.uuid,
            table_name=self.model.__tablename__,
            action="create",
        )
        return db_instance

    async def create_bulk(self, instances: List[CreateSchemaType]) -> List[ModelType]:
        """Create the new instances of the model"""
        db_instances = []
        for instance in instances:
            # Create db instance
            db_instance = self.model(**instance.dict())

            # Add in the current session
            self.session.add(db_instance)  # type: ignore
            db_instances.append(db_instance)

        # Flush the instances to the database
        await self.session.flush()  # type: ignore
        db_instances_uuids = [str(db_instance.uuid) for db_instance in db_instances]
        logger.info(f"{self.model.__tablename__}s created with uuids: {''.join(db_instances_uuids)}")

        # Log the audit logs
        for db_instance in db_instances:
            audit_logger.info(
                f"Created new {self.model.__tablename__} record with uuid: {db_instance.uuid}",
                previous_state={},
                current_state=self.get_model_instance_as_dict(db_instance),
                reference_uuid=db_instance.uuid,
                table_name=self.model.__tablename__,
                action="create",
            )
        return db_instances

    async def update(
        self,
        current_instance: ModelType,
        updated_instance: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """Update an instance of the model"""
        if not isinstance(updated_instance, dict):
            updated_instance = updated_instance.dict(exclude_unset=True)

        # Get previous state
        previous_state = self.get_model_instance_as_dict(current_instance, columns=list(updated_instance.keys()))

        # Set new values
        for field, value in updated_instance.items():
            setattr(current_instance, field, value)

        # Update value
        self.session.add(current_instance)
        await self.session.flush()

        # Update existing instance value
        await self.session.refresh(current_instance)

        # Log the audit and info logs
        message = f"Updated {self.model.__tablename__} record with uuid: {current_instance.uuid}"
        logger.info(message)
        audit_logger.info(
            message,
            previous_state=previous_state,
            current_state=updated_instance,
            reference_uuid=current_instance.uuid,
            table_name=self.model.__tablename__,
            action="update",
        )
        return current_instance

    async def update_bulk(self, filters: List, updated_values: Union[UpdateSchemaType, Dict[str, Any]]) -> None:
        """Update multiple records using filter"""
        if not isinstance(updated_values, dict):
            updated_values = updated_values.dict(exclude_unset=True)

        # Raising error if no error found
        if not filters:
            raise NoFilterFoundException(model=self.model)

        # Get current instances for audit log
        current_instances = await self.filter(filters=filters)

        # Update records in bulk
        query = update(self.model).where(*filters).values(updated_values)

        # Add audit log
        for current_instance in current_instances:
            audit_logger.info(
                f"Updated {self.model.__tablename__} record with uuid: {current_instance.uuid}",
                previous_state=self.get_model_instance_as_dict(current_instance, columns=list(updated_values.keys())),
                current_state=updated_values,
                reference_uuid=current_instance.uuid,
                table_name=self.model.__tablename__,
                action="update",
            )
        await self.session.execute(query)
        await self.session.flush()

    async def delete(self, uuid: Union[UUID, str]) -> ModelType:
        """Delete an instance of the model"""
        instance = await self.get(uuid=uuid)
        await self.session.delete(instance)
        await self.session.flush()

        # Log audit and info log
        message = f"Deleted {self.model.__tablename__} record with uuid: {uuid}"
        logger.info(message)
        audit_logger.info(
            message,
            previous_state=self.get_model_instance_as_dict(instance=instance),
            current_state=dict(),
            reference_uuid=instance.uuid,
            table_name=self.model.__tablename__,
            action="delete",
        )
        return instance

    @staticmethod
    def __add_ordered_to_query(
        query: ModelType,
        limit: int = None,
        offset: int = None,
        order_by: str = None,
        order: IOrderEnum = IOrderEnum.asc,
    ):
        """Add ordered in query"""
        # Add limit
        if limit:
            query = query.limit(limit)

        # Add offset
        if offset:
            query = query.offset(offset)

        # Order by using column
        if order_by and order == IOrderEnum.desc:
            query = query.order_by(desc(order_by))
        elif order_by:
            query = query.order_by(order_by)
        return query

    async def filter(
        self,
        filters: List,
        entities: List = None,
        limit: int = None,
        offset: int = None,
        order_by: str = None,
        order: IOrderEnum = IOrderEnum.asc,
        scalar_result: bool = False,
    ) -> Optional[Union[List[ModelType], ScalarResult]]:
        """Filter the instances using list of filters and get specifics fields/entities from database if passed"""
        # If entities not pass then fetch all the entities
        if not entities:
            entities = [self.model]

        # Create base query
        query = select(*entities).filter(*filters)

        # Add ordered details
        query = self.__add_ordered_to_query(query=query, limit=limit, offset=offset, order_by=order_by, order=order)

        # Fetch records
        result = await self.session.execute(query)

        # Scalar result allows user to fetch data according to their needs outside this function
        if scalar_result:
            return result.scalars()

        return result.scalars().all() or []

    async def get_multi_paginated_ordered(
        self,
        entities: List = None,
        filters: List = None,
        params: Optional[Params] = Params(),
        order_by: Optional[str] = None,
        order: Optional[IOrderEnum] = IOrderEnum.asc,
    ) -> Page[ModelType]:
        """Fetch the items from database in pagination format"""
        if not entities:
            entities = [self.model]

        # Create base query
        query = select(*entities)

        # Applying filters if passed
        if filters:
            query = query.filter(*filters)

        # add ordered details
        query = self.__add_ordered_to_query(query=query, order_by=order_by, order=order)

        # paginate items
        return await paginate(self.session, query, params)


class SoftDeleteBaseService(BaseService, Generic[SoftDeleteModelType, CreateSchemaType, UpdateSchemaType]):
    """
    In this base service override functions to filter soft deleted records
    """

    def _get_records_query(self, uuids: List[Union[UUID, str]]) -> Executable:
        """Build statement to get the records"""
        return select(self.model).where(self.model.uuid.in_(uuids), not_(self.model.is_deleted))

    async def get_count(self) -> int:
        """Get table record count"""
        result = await self.session.execute(
            select(func.count()).select_from(select(self.model).where(not_(self.model.is_deleted)).subquery())
        )
        return result.scalar_one()

    async def get_all(self) -> List[ModelType]:
        """Get all records from the table"""
        result = await self.session.execute(select(self.model).where(not_(self.model.is_deleted)))
        return result.scalars().all() or []

    async def update_bulk(self, filters: List, **kwargs) -> None:
        """Add soft delete filter"""
        if filters:
            filters.append(not_(self.model.is_deleted))

        await super(SoftDeleteBaseService, self).update_bulk(filters=filters, **kwargs)

    async def filter(self, filters: List, **kwargs) -> Optional[Union[List[ModelType], ScalarResult]]:
        """Add soft delete filter"""
        if filters:
            filters.append(not_(self.model.is_deleted))

        return await super(SoftDeleteBaseService, self).filter(filters=filters, **kwargs)

    async def get_multi_paginated_ordered(
        self, entities: List = None, filters: List = None, **kwargs
    ) -> Page[ModelType]:
        """Add soft delete filter"""
        if filters:
            filters.append(not_(self.model.is_deleted))
        else:
            filters = [not_(self.model.is_deleted)]

        return await super(SoftDeleteBaseService, self).get_multi_paginated_ordered(
            entities=entities, filters=filters, **kwargs
        )

    async def delete(self, uuid: Union[UUID, str]) -> ModelType:
        """Soft delete an instance of the model"""
        # Get instance
        instance = await self.get(uuid=uuid)

        # Update is_deleted to True
        updated_instance_dict = dict(is_deleted=True)
        _ = await self.update(current_instance=instance, updated_instance=updated_instance_dict)

        # Log audit and info log
        message = f"Soft Deleted {self.model.__tablename__} record with uuid: {uuid}"
        logger.info(message)
        audit_logger.info(
            message,
            previous_state=dict(is_deleted=instance.is_deleted),
            current_state=updated_instance_dict,
            reference_uuid=instance.uuid,
            table_name=self.model.__tablename__,
            action="delete",
        )
        return instance
