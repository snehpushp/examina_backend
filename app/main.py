from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from loguru import logger

from app.api import api_routers
from app.config import configuration


def get_application():
    # Core Application Instance
    logger.info("Creating core application instance")
    _app = FastAPI(
        title=configuration.PROJECT_NAME,
        debug=configuration.PROJECT_DEBUG,
        version=configuration.PROJECT_API_VERSION,
    )

    # Add routers
    _app.include_router(api_routers)

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
    )

    # Add API pagination
    add_pagination(_app)

    logger.info("Core application instance created successfully")
    return _app


app = get_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=configuration.PROJECT_HOST, port=configuration.PROJECT_PORT)
