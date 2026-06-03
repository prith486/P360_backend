from typing import List, Dict
import sys
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ConfigValidator:
    """Validate environment configuration on startup."""
    
    @staticmethod
    def validate_or_exit() -> None:
        """Validate configuration and exit if critical errors found."""
        errors = []
        warnings = []
        
        # Critical checks
        if len(settings.SECRET_KEY) < 32:
            errors.append("SECRET_KEY is too short (min 32 chars)")
            
        if settings.is_production and settings.DEBUG:
            errors.append("DEBUG mode enabled in production")
            
        # Warning checks
        if not settings.OPENAI_API_KEY and not settings.ANTHROPIC_API_KEY:
            warnings.append("No AI API keys configured - AI features will be disabled")
            
        if not settings.SENDGRID_API_KEY or "your-" in settings.SENDGRID_API_KEY:
             warnings.append("SENDGRID_API_KEY not configured properly")

        # Report
        if warnings:
            logger.warning("CONFIGURATION WARNINGS:")
            for w in warnings:
                logger.warning(f"  ⚠ {w}")
                
        if errors:
            logger.error("CONFIGURATION ERRORS:")
            for e in errors:
                logger.error(f"  ✗ {e}")
            logger.critical("Startup aborted due to configuration errors")
            sys.exit(1)
            
        logger.info("✓ All configuration checks passed")

config_validator = ConfigValidator()
