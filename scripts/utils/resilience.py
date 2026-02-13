"""
Resilience Utilities for BrowserOS Automation Scripts

This module provides bulletproof patterns for:
- Exponential backoff retry logic
- API key validation
- Structured logging
- Graceful degradation
- Network request resilience
"""

import time
import logging
import functools
import re
from typing import Callable, Any, Optional, Union


class ResilientLogger:
    """Structured logger with consistent formatting across all scripts."""
    
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Console handler with formatting
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, msg: str, **kwargs):
        self.logger.info(msg, **kwargs)
    
    def warn(self, msg: str, **kwargs):
        self.logger.warning(msg, **kwargs)
    
    def error(self, msg: str, exc_info: bool = False, **kwargs):
        self.logger.error(msg, exc_info=exc_info, **kwargs)
    
    def debug(self, msg: str, **kwargs):
        self.logger.debug(msg, **kwargs)
    
    def critical(self, msg: str, exc_info: bool = False, **kwargs):
        self.logger.critical(msg, exc_info=exc_info, **kwargs)


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator that implements exponential backoff retry logic.
    
    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay between retries (default: 30.0)
        exponential_base: Base for exponential calculation (default: 2.0)
        exceptions: Tuple of exception types to catch (default: Exception)
    
    Example:
        @retry_with_backoff(max_attempts=3, base_delay=2.0)
        def fetch_data():
            return requests.get(url, timeout=10)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = ResilientLogger(func.__module__)
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}",
                            exc_info=True
                        )
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base ** (attempt - 1)), max_delay)
                    logger.warn(
                        f"{func.__name__} attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
            
            return None  # Should never reach here
        
        return wrapper
    return decorator


def validate_api_key(
    key: Optional[str],
    key_name: str = "API_KEY",
    min_length: int = 20,
    allow_placeholder: bool = False
) -> bool:
    """
    Validates an API key with configurable rules.
    
    Args:
        key: The API key to validate
        key_name: Name of the key for error messages
        min_length: Minimum acceptable length
        allow_placeholder: Whether to accept placeholder values
    
    Returns:
        bool: True if valid, False otherwise
    
    Raises:
        ValueError: If key is invalid and not allowing placeholders
    """
    if not key:
        raise ValueError(f"{key_name} is not set")
    
    # Check for common placeholder patterns
    placeholder_patterns = [
        r'your[-_].*[-_]key',
        r'replace[-_]me',
        r'example[-_]key',
        r'placeholder',
        r'xxx+',
        r'000+'
    ]
    
    is_placeholder = any(re.search(pattern, key.lower()) for pattern in placeholder_patterns)
    
    if is_placeholder:
        if not allow_placeholder:
            raise ValueError(f"{key_name} appears to be a placeholder value: {key[:20]}...")
        return False
    
    # Validate length
    if len(key) < min_length:
        raise ValueError(f"{key_name} is too short (minimum {min_length} characters)")
    
    # Validate format (should contain alphanumeric and possibly special chars)
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', key):
        raise ValueError(f"{key_name} contains invalid characters")
    
    return True


def safe_json_load(data: str, default: Any = None, logger: Optional[ResilientLogger] = None) -> Any:
    """
    Safely parse JSON with fallback value.
    
    Args:
        data: JSON string to parse
        default: Default value if parsing fails
        logger: Optional logger for error reporting
    
    Returns:
        Parsed JSON or default value
    """
    import json
    
    try:
        return json.loads(data)
    except (json.JSONDecodeError, ValueError) as e:
        if logger:
            logger.warn(f"JSON parsing failed: {e}. Using default value.")
        return default


def safe_file_write(
    filepath: str,
    content: str,
    mode: str = 'w',
    encoding: str = 'utf-8',
    create_dirs: bool = True,
    logger: Optional[ResilientLogger] = None
) -> bool:
    """
    Safely write to file with error handling and directory creation.
    
    Args:
        filepath: Path to file
        content: Content to write
        mode: File mode ('w' or 'a')
        encoding: File encoding
        create_dirs: Whether to create parent directories
        logger: Optional logger for error reporting
    
    Returns:
        bool: True if successful, False otherwise
    """
    import os
    from pathlib import Path
    
    try:
        if create_dirs:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, mode, encoding=encoding) as f:
            f.write(content)
        
        return True
    except (IOError, OSError) as e:
        if logger:
            logger.error(f"Failed to write to {filepath}: {e}", exc_info=True)
        return False


def safe_file_read(
    filepath: str,
    default: str = "",
    encoding: str = 'utf-8',
    logger: Optional[ResilientLogger] = None
) -> str:
    """
    Safely read from file with fallback value.
    
    Args:
        filepath: Path to file
        default: Default value if read fails
        encoding: File encoding
        logger: Optional logger for error reporting
    
    Returns:
        File content or default value
    """
    from pathlib import Path
    
    try:
        return Path(filepath).read_text(encoding=encoding)
    except (FileNotFoundError, IOError, OSError) as e:
        if logger:
            logger.warn(f"Failed to read {filepath}: {e}. Using default value.")
        return default


def resilient_request(
    url: str,
    method: str = 'GET',
    timeout: int = 30,
    max_attempts: int = 3,
    **kwargs
) -> Optional[Any]:
    """
    Make HTTP request with automatic retry and timeout.
    
    Args:
        url: URL to request
        method: HTTP method (GET, POST, etc.)
        timeout: Request timeout in seconds
        max_attempts: Maximum retry attempts
        **kwargs: Additional arguments for requests
    
    Returns:
        Response object or None if all attempts fail
    """
    import requests
    
    @retry_with_backoff(
        max_attempts=max_attempts,
        exceptions=(requests.RequestException, requests.Timeout)
    )
    def _make_request():
        return requests.request(method, url, timeout=timeout, **kwargs)
    
    try:
        return _make_request()
    except Exception:
        return None


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL string to validate
    
    Returns:
        bool: True if valid URL, False otherwise
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return bool(url_pattern.match(url))


def check_dependencies(dependencies: list, logger: Optional[ResilientLogger] = None) -> tuple[list, list]:
    """
    Check which dependencies are installed.
    
    Args:
        dependencies: List of package names to check
        logger: Optional logger for reporting
    
    Returns:
        tuple: (installed_packages, missing_packages)
    """
    import importlib
    
    installed = []
    missing = []
    
    for dep in dependencies:
        try:
            importlib.import_module(dep)
            installed.append(dep)
        except ImportError:
            missing.append(dep)
            if logger:
                logger.warn(f"Missing dependency: {dep}")
    
    return installed, missing


if __name__ == "__main__":
    # Self-test
    logger = ResilientLogger(__name__)
    logger.info("Resilience utilities loaded successfully")
    
    # Test API key validation
    try:
        validate_api_key("short", "TEST_KEY")
    except ValueError as e:
        logger.info(f"Correctly rejected short key: {e}")
    
    try:
        validate_api_key("your-api-key-here", "TEST_KEY")
    except ValueError as e:
        logger.info(f"Correctly rejected placeholder: {e}")
    
    # Test URL validation
    assert validate_url("https://example.com")
    assert validate_url("http://localhost:3000")
    assert not validate_url("not-a-url")
    logger.info("URL validation working")
    
    logger.info("All self-tests passed")
