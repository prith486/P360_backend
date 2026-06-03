import logging
import sys
from app.core.config import settings

# Log formats
PRODUCTION_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | "
    "%(funcName)s:%(lineno)d | %(message)s"
)
DEVELOPMENT_LOG_FORMAT = "%(levelname)s:     %(name)s - %(message)s"

def setup_logging() -> None:
    """Configure application logging based on environment."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    if settings.is_production:
        log_format = PRODUCTION_LOG_FORMAT
    else:
        log_format = DEVELOPMENT_LOG_FORMAT
    
    # Use standard sys.stdout. Let Uvicorn handle its own stdout wrapping.
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(log_format))

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[handler]
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(
        logging.WARNING if settings.is_production else logging.INFO
    )
    
    if settings.is_production:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    logging.info("Logging configured successfully")

class StructuredLogger:
    """Structured logger for consistent formatting."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, kwargs)
    
    def error(self, message: str, **kwargs):
        self._log(logging.ERROR, message, kwargs)
    
    def debug(self, message: str, **kwargs):
        self._log(logging.DEBUG, message, kwargs)

    def critical(self, message: str, **kwargs):  # Added critical method for parity
        self._log(logging.CRITICAL, message, kwargs)
    
    def _log(self, level: int, message: str, context: dict):
        if context:
            # Flatten context into a string representation
            context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
            full_message = f"{message} | {context_str}"
        else:
            full_message = message
        self.logger.log(level, full_message)

def get_logger(name: str) -> StructuredLogger:
    """Get structured logger instance."""
    return StructuredLogger(name)
