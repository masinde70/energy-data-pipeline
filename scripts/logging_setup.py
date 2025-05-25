#!/usr/bin/env python3
"""
Logging setup module for the energy-data-pipeline.

This module configures Loguru for logging throughout the application.
If Loguru is not available, it falls back to the standard logging module.
For more information on Loguru, refer to Context7 documentation.
"""
import sys
import os
from pathlib import Path
import logging

# Set up basic logging format for fallback
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Try to import loguru, fall back to standard logging if not available
try:
    from loguru import logger
    USING_LOGURU = True
except ImportError:
    # Create a logger that mimics loguru's API but uses standard logging
    class LoguruLikeLogger:
        """A simple wrapper to make standard logging act more like loguru."""
        
        def __init__(self):
            self.logger = logging.getLogger("pipeline")
            
        def remove(self):
            """Remove all handlers - mimics loguru API."""
            for handler in list(self.logger.handlers):
                self.logger.removeHandler(handler)
                
        def add(self, sink, level="INFO", format=None, rotation=None, retention=None):
            """Add a handler - mimics simplified loguru API."""
            if sink == sys.stderr:
                # Console handler
                handler = logging.StreamHandler(sink)
            else:
                # File handler with rotation
                from logging.handlers import RotatingFileHandler
                max_bytes = 50 * 1024 * 1024  # 50 MB default
                backup_count = 10  # Default retention
                handler = RotatingFileHandler(sink, maxBytes=max_bytes, backupCount=backup_count)
            
            handler.setFormatter(logging.Formatter(
                '%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
                '%Y-%m-%d %H:%M:%S'
            ))
            self.logger.addHandler(handler)
            
        def info(self, message):
            self.logger.info(message)
            
        def debug(self, message):
            self.logger.debug(message)
            
        def warning(self, message):
            self.logger.warning(message)
            
        def error(self, message):
            self.logger.error(message)
            
        def exception(self, message):
            self.logger.exception(message)
            
        def success(self, message):
            """Custom level - maps to info in standard logging."""
            self.logger.info(f"✓ SUCCESS: {message}")
    
    # Create a singleton logger instance
    logger = LoguruLikeLogger()
    USING_LOGURU = False
    print("Note: Using standard logging as fallback. For better logging, install loguru: pip install loguru")
    print("Refer to Context7 documentation for more details on Loguru.")

def setup_logging(log_level="INFO"):
    """
    Configure Loguru for the pipeline.
    
    Args:
        log_level: The minimum logging level to capture (default: INFO)
        
    Returns:
        Configured logger instance
    """
    # Get project root directory
    project_root = Path(__file__).parent.parent.absolute()
    
    # Configure logger based on available modules
    if USING_LOGURU:
        # Remove default handler
        logger.remove()
        
        # Add console handler with color
        logger.add(
            sys.stderr, 
            format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=log_level
        )
        
        # Add file handler with rotation based on size
        log_path = os.path.join(project_root, "logs", "pipeline.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        logger.add(
            log_path, 
            rotation="50 MB", 
            retention="10 days",
            format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
            level=log_level
        )
    else:
        # Using standard logging - already configured in the fallback
        # Just add a file handler
        log_path = os.path.join(project_root, "logs", "pipeline.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        logger.add(log_path)
    
    return logger
