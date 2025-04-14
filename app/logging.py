from functools import wraps
from typing import Callable

import structlog

def setup_logging():
    """Configure structured logging"""
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )
    return structlog.get_logger()

logger = setup_logging()

def log_endpoint(event_name: str):
    """Decorator for endpoint logging"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log_context = {k: v for k, v in kwargs.items()
                           if isinstance(v, (str, int, float, bool))}
            logger.info(f"{event_name}_started", **log_context)

            try:
                result = func(*args, **kwargs)

                if isinstance(result, dict) and "id" in result:
                    log_context["id"] = result["id"]
                elif hasattr(result, "id"):
                    log_context["id"] = result.id

                if isinstance(result, list):
                    log_context["count"] = len(result)

                logger.info(f"{event_name}_completed", **log_context)
                return result
            except Exception as e:
                logger.error(f"{event_name}_failed", error=str(e), **log_context)
                raise

        return wrapper
    return decorator
