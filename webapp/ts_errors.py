"""
TowerScout Error Handling System

This module provides a comprehensive hierarchy of custom exceptions for TowerScout,
enabling structured error handling and better debugging capabilities.

Author: TowerScout Development Team
Date: December 2025
"""

import traceback
from typing import Optional, Dict, Any
from datetime import datetime
import re


def _sanitize_error_detail(value: Any) -> Any:
    """Redact provider credentials from structured error responses."""
    if isinstance(value, dict):
        return {key: _sanitize_error_detail(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize_error_detail(item) for item in value]
    if not isinstance(value, str):
        return value

    value = re.sub(r'AIza[0-9A-Za-z\-_]{35}', 'AIza***REDACTED***', value)
    value = re.sub(r'subscription-key=[0-9A-Za-z\-_]+', 'subscription-key=***REDACTED***', value)
    value = re.sub(
        r'([?&])(key|apikey|api_key|token|access_token)=([^&\s]+)',
        r'\1\2=***REDACTED***',
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(r'Authorization:\s*[^\s]+', 'Authorization: ***REDACTED***', value, flags=re.IGNORECASE)
    return value


class TowerScoutError(Exception):
    """
    Base exception class for all TowerScout-specific errors.
    
    Provides structured error information including error codes, user-friendly messages,
    and technical details for debugging.
    """
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None, 
                 user_message: str = None, cause: Exception = None):
        """
        Initialize TowerScout error.
        
        Args:
            message: Technical error message for developers
            error_code: Unique identifier for this error type
            details: Additional context information
            user_message: User-friendly error message
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.user_message = user_message or "An error occurred while processing your request."
        self.cause = cause
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.traceback = traceback.format_exc() if cause else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON serialization."""
        error_dict = {
            "error": True,
            "type": self.__class__.__name__,
            "code": self.error_code,
            "message": self.user_message,
            "technical_message": _sanitize_error_detail(self.message),
            "timestamp": self.timestamp,
            "details": _sanitize_error_detail(self.details)
        }
        
        if self.cause:
            error_dict["cause"] = {
                "type": self.cause.__class__.__name__,
                "message": _sanitize_error_detail(str(self.cause))
            }
            
        return error_dict


class ConfigurationError(TowerScoutError):
    """Raised when there are configuration issues (missing API keys, invalid settings)."""
    
    def __init__(self, message: str, missing_config: str = None, **kwargs):
        kwargs.setdefault("user_message", "Configuration error. Please check your settings and try again.")
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            **kwargs
        )
        if missing_config:
            self.details["missing_config"] = missing_config


class ModelLoadError(TowerScoutError):
    """Raised when ML models fail to load (missing files, CUDA issues, corrupted weights)."""
    
    def __init__(self, message: str, model_name: str = None, model_path: str = None, **kwargs):
        kwargs.setdefault("user_message", "Model loading failed. The detection system may be temporarily unavailable.")
        super().__init__(
            message=message,
            error_code="MODEL_LOAD_ERROR",
            **kwargs
        )
        if model_name:
            self.details["model_name"] = model_name
        if model_path:
            self.details["model_path"] = model_path


class MapProviderError(TowerScoutError):
    """Raised when map provider APIs fail (rate limits, authentication, network issues)."""
    
    def __init__(self, message: str, provider: str = None, api_response_code: int = None, 
                 retry_after: int = None, **kwargs):
        kwargs.setdefault("user_message", "Map service temporarily unavailable. Please try again in a moment.")
        super().__init__(
            message=message,
            error_code="MAP_PROVIDER_ERROR",
            **kwargs
        )
        if provider:
            self.details["provider"] = provider
        if api_response_code:
            self.details["response_code"] = api_response_code
        if retry_after:
            self.details["retry_after"] = retry_after


class ProcessingError(TowerScoutError):
    """Raised during image processing, detection, or coordinate transformation operations."""
    
    def __init__(self, message: str, operation: str = None, tile_count: int = None, **kwargs):
        kwargs.setdefault("user_message", "Processing failed. Please check your input and try again.")
        super().__init__(
            message=message,
            error_code="PROCESSING_ERROR",
            **kwargs
        )
        if operation:
            self.details["operation"] = operation
        if tile_count:
            self.details["tile_count"] = tile_count


class SessionError(TowerScoutError):
    """Raised when session management fails (expired sessions, invalid state)."""
    
    def __init__(self, message: str, session_id: str = None, **kwargs):
        kwargs.setdefault("user_message", "Session error. Please refresh the page and try again.")
        super().__init__(
            message=message,
            error_code="SESSION_ERROR",
            **kwargs
        )
        if session_id:
            self.details["session_id"] = session_id


class ValidationError(TowerScoutError):
    """Raised when input validation fails (already exists but enhancing for consistency)."""
    
    def __init__(self, message: str, field_name: str = None, field_value: Any = None, **kwargs):
        # Import existing ValidationError behavior if it exists
        kwargs.setdefault("user_message", f"Invalid input: {message}")
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            **kwargs
        )
        if field_name:
            self.details["field_name"] = field_name
        if field_value is not None:
            self.details["field_value"] = str(field_value)


class NetworkError(TowerScoutError):
    """Raised when network operations fail (timeouts, connection errors)."""
    
    def __init__(self, message: str, url: str = None, timeout: int = None, **kwargs):
        kwargs.setdefault("user_message", "Network connection failed. Please check your internet connection and try again.")
        super().__init__(
            message=message,
            error_code="NETWORK_ERROR",
            **kwargs
        )
        if url:
            self.details["url"] = url
        if timeout:
            self.details["timeout"] = timeout


class ResourceError(TowerScoutError):
    """Raised when system resources are insufficient (disk space, memory, GPU)."""
    
    def __init__(self, message: str, resource_type: str = None, available: str = None, 
                 required: str = None, **kwargs):
        kwargs.setdefault("user_message", "Insufficient system resources. Please try with a smaller area or contact support.")
        super().__init__(
            message=message,
            error_code="RESOURCE_ERROR",
            **kwargs
        )
        if resource_type:
            self.details["resource_type"] = resource_type
        if available:
            self.details["available"] = available
        if required:
            self.details["required"] = required


def create_error_response(error: Exception) -> Dict[str, Any]:
    """
    Create standardized error response dictionary from any exception.
    
    Args:
        error: Exception to convert to response
        
    Returns:
        Dictionary suitable for JSON serialization
    """
    if isinstance(error, TowerScoutError):
        return error.to_dict()
    else:
        # Handle non-TowerScout exceptions
        return {
            "error": True,
            "type": error.__class__.__name__,
            "code": "UNKNOWN_ERROR",
            "message": "An unexpected error occurred. Please try again or contact support.",
            "technical_message": str(error),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "details": {}
        }


def wrap_external_call(func, error_class: type = TowerScoutError, **error_kwargs):
    """
    Decorator to wrap external API calls with proper exception handling.
    
    Args:
        func: Function to wrap
        error_class: TowerScout exception class to raise on failure
        **error_kwargs: Additional arguments for the exception
        
    Returns:
        Wrapped function that raises TowerScout exceptions
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise error_class(
                message=f"External call failed: {func.__name__}",
                cause=e,
                **error_kwargs
            )
    
    return wrapper
