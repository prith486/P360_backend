import logging
import sys
from app.core.config import settings

# Configure structured logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


def get_logger(name: str) -> logging.Logger:
    """Get logger instance for module."""
    return logging.getLogger(name)
