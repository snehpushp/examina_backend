import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute

from app.logger import logger


class ExaminaRouteWrapper(APIRoute):
    """
    Created this custom route wrapper for following reasons:
    1) For audit trail logging
    """

    def get_route_handler(self) -> Callable:
        """Override the default route handler to add audit trail logging information"""
        # Get the original route handler
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            """Custom route handler to add audit trail logging information"""
            # Reading information from the request header
            user_login_id = request.headers.get("x-user-login-id")
            user_qid = request.headers.get("x-user-qid")
            user_email_id = request.headers.get("x-user-email-id")
            user_name = request.headers.get("x-user-name")
            trace_id = request.headers.get("x-trace-id") or str(uuid.uuid4())

            # Setting the information in the in loguru logger
            with logger.contextualize(
                user_login_id=user_login_id,
                user_qid=user_qid,
                user_email_id=user_email_id,
                user_name=user_name,
                trace_id=trace_id,
            ):
                # Call original route handler
                try:
                    return await original_route_handler(request)
                except Exception as e:
                    # Log the exception
                    message = "Error occurred while processing the request"
                    logger.exception(message)
                    logger.exception(
                        getattr(e, "detail", None) or str(e),
                        error_code=getattr(e, "status_code", None),
                    )
                    raise e

        return custom_route_handler
