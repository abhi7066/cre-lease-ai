"""
Logging configuration for the application
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from ..config.settings import Settings


def setup_logger(name: str = "lease_extractor", log_file: str = None) -> logging.Logger:
    """
    Setup application logger with console and file handlers
    
    Args:
        name: Logger name
        log_file: Log file name (optional, will be auto-generated if None)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, Settings.LOG_LEVEL))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"lease_extraction_{timestamp}.log"
    
    Settings.ensure_directories()
    file_path = Settings.LOGS_DIR / log_file
    
    file_handler = logging.FileHandler(file_path, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        Settings.LOG_FORMAT,
        datefmt=Settings.LOG_DATE_FORMAT
    )
    file_handler.setFormatter(file_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "lease_extractor") -> logging.Logger:
    """Get existing logger or create new one"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger
