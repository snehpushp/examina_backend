from pydantic import BaseSettings

from app.constants import CONFIGMAP_PATH


class Settings(BaseSettings):
    class Config:
        case_sensitive = True
        env_file = CONFIGMAP_PATH


class AppSettings(Settings):
    PROJECT_NAME: str
    PROJECT_DEBUG: str
    PROJECT_API_VERSION: str
    PROJECT_HOST: str = "0.0.0.0"
    PROJECT_PORT: int = 8001
    AUDIT_LOG_LOCATION: str


class PostgresSettings(Settings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DATABASE: str
    POSTGRES_DATABASE_SCHEMA: str


class Configuration(AppSettings, PostgresSettings):
    """
    This is where we accumulate all the settings and create one class to access them
    """


# App related settings
configuration = Configuration()
