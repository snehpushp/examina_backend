from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import configuration

# creating sync sqlalchemy session
SQLALCHEMY_DATABASE_URL = URL.create(
    "postgresql+psycopg2",
    username=configuration.POSTGRES_USER,
    password=configuration.POSTGRES_PASSWORD,
    host=configuration.POSTGRES_HOST,
    database=configuration.POSTGRES_DATABASE,
    port=configuration.POSTGRES_PORT,
)
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, echo=False)
session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


# Below code used for creating async sqlalchemy session
ASYNC_SQLALCHEMY_DATABASE_URL = URL.create(
    "postgresql+asyncpg",
    username=configuration.POSTGRES_USER,
    password=configuration.POSTGRES_PASSWORD,
    host=configuration.POSTGRES_HOST,
    database=configuration.POSTGRES_DATABASE,
    port=configuration.POSTGRES_PORT,
)
async_engine = create_async_engine(ASYNC_SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, echo=False)
async_session_maker = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    expire_on_commit=False,
)


class SessionContextManager:
    """
    A context manager that manages a SQLAlchemy session.

    Example usage:
        with SessionContextManager() as session:
            doc something with the session
    """

    def __enter__(self):
        """Create a new session"""
        logger.info("Initializing the sqlalchemy session")
        self.session = session_maker()
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        """Close the session and if an exception was raised in the `with` block, so roll back the transaction"""
        # Roll back the transaction if error raised
        if exc_type is not None:
            # An exception was raised in the `with` block, so roll back the transaction
            self.session.rollback()
            logger.error(
                f"Exception raised in SQLAlchemy session. Rolling back transaction.\n"
                f"Error value: {exc_value}\n"
                f"Traceback: {traceback}"
            )

        self.session.close()
        logger.info("Closing the sqlalchemy session")


def get_session():
    """This method use as Dependencies in api"""
    # Create a session
    logger.info("Initializing the sqlalchemy session")
    session = session_maker()

    try:
        yield session
    finally:
        session.close()
        logger.info("Closing the sqlalchemy session")


async def get_async_session() -> AsyncSession:
    logger.debug("Initializing the sqlalchemy async session")
    async with async_session_maker() as async_session:
        async with async_session.begin():
            yield async_session
