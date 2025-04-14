import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.logging import logger

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging with unique request IDs"""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        request.state.start_time = time.time()

        logger.info(
            "request_started",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host,
        )

        try:
            response = await call_next(request)

            logger.info(
                "request_completed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round((time.time() - request.state.start_time) * 1000, 2),
            )

            return response
        except Exception as e:
            logger.error(
                "request_failed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration_ms=round((time.time() - request.state.start_time) * 1000, 2),
            )
            raise
