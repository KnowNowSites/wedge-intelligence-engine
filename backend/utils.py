"""
Shared utilities for scrapers: logging, retries, delays, and error handling.
"""

import logging
import random
import time
from pathlib import Path
from functools import wraps
from typing import Callable, Any, TypeVar

# Setup logging directory
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Configure logger
logger = logging.getLogger("wie")
logger.setLevel(logging.DEBUG)

# File handler for scraper errors
error_handler = logging.FileHandler(LOG_DIR / "scraper_errors.log")
error_handler.setLevel(logging.ERROR)

# File handler for all logs
file_handler = logging.FileHandler(LOG_DIR / "scraper.log")
file_handler.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
error_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(error_handler)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def randomized_delay(min_seconds: float = 2, max_seconds: float = 5) -> None:
    """
    Apply a randomized delay to respect rate limits.
    Default: 2-5 seconds.
    """
    delay = random.uniform(min_seconds, max_seconds)
    logger.debug(f"Applying delay: {delay:.2f}s")
    time.sleep(delay)


T = TypeVar("T")


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for exponential backoff retry logic.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each retry
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = base_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    logger.debug(f"Attempt {attempt + 1}/{max_retries + 1} for {func.__name__}")
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )
            
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


def safe_scraper_execution(scraper_name: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to ensure one scraper failure does not crash others.
    Logs errors and returns empty list on failure.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T | list]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T | list:
            try:
                logger.info(f"Starting {scraper_name}")
                result = func(*args, **kwargs)
                logger.info(f"Completed {scraper_name}")
                return result
            except Exception as e:
                logger.error(f"Scraper {scraper_name} failed: {e}", exc_info=True)
                return []
        
        return wrapper
    return decorator


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module."""
    return logging.getLogger(f"wie.{name}")
