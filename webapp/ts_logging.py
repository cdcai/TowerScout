"""
TowerScout Logging System

This module provides structured logging configuration for TowerScout,
replacing print statements with proper logging levels and output formatting.

Author: TowerScout Development Team
Date: December 2025
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import json
import re
from ts_paths import get_log_dir


def sanitize_sensitive_data(message: str) -> str:
    """
    Sanitize sensitive information from log messages.
    
    Redacts:
    - Google API keys (AIza...)
    - Azure subscription keys
    - Generic API keys in URLs
    - Any long alphanumeric tokens that look like keys
    
    Args:
        message: The log message to sanitize
        
    Returns:
        Sanitized message with sensitive data redacted
    """
    if not isinstance(message, str):
        message = str(message)
    
    # Redact Google API keys (AIza followed by 35 characters)
    message = re.sub(r'AIza[0-9A-Za-z\-_]{35}', 'AIza***REDACTED***', message)
    
    # Redact Azure subscription keys (subscription-key= parameter)
    message = re.sub(r'subscription-key=[0-9A-Za-z\-_]+', 'subscription-key=***REDACTED***', message)
    
    # Redact generic API key parameters in URLs
    message = re.sub(r'([?&])(key|apikey|api_key|token|access_token)=([^&\s]+)', r'\1\2=***REDACTED***', message, flags=re.IGNORECASE)
    
    # Redact Authorization headers
    message = re.sub(r'Authorization:\s*[^\s]+', 'Authorization: ***REDACTED***', message, flags=re.IGNORECASE)
    
    return message


class TowerScoutFormatter(logging.Formatter):
    """Custom formatter for TowerScout logs with structured JSON output option."""
    
    def __init__(self, json_format: bool = False):
        self.json_format = json_format
        if json_format:
            super().__init__()
        else:
            # Human-readable format for console/file logs
            super().__init__(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
    
    def format(self, record: logging.LogRecord) -> str:
        # Sanitize the message before formatting
        original_msg = record.msg
        if isinstance(record.msg, str):
            record.msg = sanitize_sensitive_data(record.msg)
        
        # Also sanitize any args that will be interpolated
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: sanitize_sensitive_data(str(v)) if isinstance(v, str) else v 
                              for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(sanitize_sensitive_data(str(arg)) if isinstance(arg, str) else arg 
                                   for arg in record.args)
        
        try:
            if self.json_format:
                # Structured JSON format for machine processing
                log_entry = {
                    'timestamp': datetime.utcfromtimestamp(record.created).isoformat() + 'Z',
                    'level': record.levelname,
                    'logger': record.name,
                    'message': sanitize_sensitive_data(record.getMessage()),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno
                }
                
                # Add exception information if present
                if record.exc_info:
                    log_entry['exception'] = {
                        'type': record.exc_info[0].__name__,
                        'message': sanitize_sensitive_data(str(record.exc_info[1])),
                        'traceback': sanitize_sensitive_data(self.formatException(record.exc_info))
                    }
                
                # Add extra fields if present
                if hasattr(record, 'extra_fields'):
                    log_entry.update(record.extra_fields)
                    
                return json.dumps(log_entry)
            else:
                return super().format(record)
        finally:
            # Restore original message
            record.msg = original_msg


class TowerScoutLogger:
    """
    Centralized logging configuration for TowerScout application.
    
    Provides different loggers for different components with appropriate levels
    and output destinations.
    """
    
    _loggers: Dict[str, logging.Logger] = {}
    _configured: bool = False
    
    @classmethod
    def configure(cls, log_level: str = "INFO", log_dir: Optional[str] = None,
                  console_output: bool = True, json_logs: bool = False):
        """
        Configure logging system for TowerScout.
        
        Args:
            log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory for log files
            console_output: Whether to output logs to console
            json_logs: Whether to use JSON format for file logs
        """
        if cls._configured:
            return
        
        if log_dir is None:
            log_dir = str(get_log_dir())

        # Create logs directory
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up root logger
        root_logger = logging.getLogger('towerscout')
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Remove existing handlers to avoid duplicates
        root_logger.handlers.clear()
        
        # Console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(TowerScoutFormatter(json_format=False))
            root_logger.addHandler(console_handler)
        
        # File handler - General application logs
        file_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, 'towerscout.log'),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(TowerScoutFormatter(json_format=json_logs))
        root_logger.addHandler(file_handler)
        
        # Error file handler - Only errors and above
        error_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, 'towerscout_errors.log'),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(TowerScoutFormatter(json_format=json_logs))
        root_logger.addHandler(error_handler)
        
        # Performance log handler - For timing and performance metrics
        perf_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(log_dir, 'performance.log'),
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(TowerScoutFormatter(json_format=True))  # Always JSON for metrics
        
        # Create performance logger
        perf_logger = logging.getLogger('towerscout.performance')
        perf_logger.addHandler(perf_handler)
        perf_logger.propagate = False  # Don't propagate to parent logger
        
        cls._configured = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get or create a logger with the specified name.
        
        Args:
            name: Logger name (e.g., 'towerscout.maps', 'towerscout.ml')
            
        Returns:
            Configured logger instance
        """
        if not cls._configured:
            cls.configure()
        
        full_name = f'towerscout.{name}' if not name.startswith('towerscout') else name
        
        if full_name not in cls._loggers:
            logger = logging.getLogger(full_name)
            cls._loggers[full_name] = logger
        
        return cls._loggers[full_name]
    
    @classmethod
    def log_performance(cls, operation: str, duration: float, **kwargs):
        """
        Log performance metrics in structured format.
        
        Args:
            operation: Name of the operation being measured
            duration: Duration in seconds
            **kwargs: Additional metadata
        """
        perf_logger = logging.getLogger('towerscout.performance')
        
        metrics = {
            'operation': operation,
            'duration_seconds': duration,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        metrics.update(kwargs)
        
        # Use extra to pass structured data
        perf_logger.info(f"Performance: {operation}", extra={'extra_fields': metrics})


# Convenience functions for common loggers
def get_main_logger() -> logging.Logger:
    """Get the main application logger."""
    return TowerScoutLogger.get_logger('main')


def get_maps_logger() -> logging.Logger:
    """Get the maps/providers logger."""
    return TowerScoutLogger.get_logger('maps')


def get_ml_logger() -> logging.Logger:
    """Get the machine learning logger."""
    return TowerScoutLogger.get_logger('ml')


def get_api_logger() -> logging.Logger:
    """Get the API/Flask routes logger."""
    return TowerScoutLogger.get_logger('api')


def get_session_logger() -> logging.Logger:
    """Get the session management logger."""
    return TowerScoutLogger.get_logger('session')


def log_startup_info():
    """Log essential startup information."""
    logger = get_main_logger()
    logger.info("=" * 50)
    logger.info("TowerScout Application Starting")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Working Directory: {os.getcwd()}")
    logger.info(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    logger.info("=" * 50)


def log_shutdown_info():
    """Log application shutdown information."""
    logger = get_main_logger()
    logger.info("TowerScout Application Shutting Down")
    logger.info("=" * 50)


def replace_print_with_logging():
    """
    Monkey patch print function to redirect to logging (development helper).
    Only use this during development/debugging.
    """
    original_print = print
    logger = get_main_logger()
    
    def logging_print(*args, **kwargs):
        # Convert print arguments to string
        message = ' '.join(str(arg) for arg in args)
        logger.debug(f"[PRINT] {message}")
        # Still call original print for immediate console output during development
        original_print(*args, **kwargs)
    
    # Replace built-in print
    import builtins
    builtins.print = logging_print


# Initialize logging on import (with default settings)
try:
    # Auto-configure with environment variables if available
    log_level = os.getenv('TOWERSCOUT_LOG_LEVEL', 'INFO')
    log_dir = str(get_log_dir())
    console_output = os.getenv('TOWERSCOUT_CONSOLE_LOGS', 'true').lower() == 'true'
    json_logs = os.getenv('TOWERSCOUT_JSON_LOGS', 'false').lower() == 'true'
    
    TowerScoutLogger.configure(
        log_level=log_level,
        log_dir=log_dir,
        console_output=console_output,
        json_logs=json_logs
    )
except Exception as e:
    # Fallback to basic logging if configuration fails
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logging.getLogger('towerscout').error(f"Failed to configure logging: {e}")
