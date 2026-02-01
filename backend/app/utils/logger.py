"""Structured logging configuration.

Provides consistent logging format and level management across the application.
Includes request/response logging and performance monitoring.
"""

import logging
import os
import time
import json
from logging.handlers import RotatingFileHandler
from typing import Dict, Any
from datetime import datetime


# Get log level from environment or default to INFO
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def setup_logging(name: str) -> logging.Logger:
    """Configure and return a logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL))

    # Console handler with structured formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_LEVEL))

    # Structured formatter with JSON support
    if os.getenv("JSON_LOGGING", "false").lower() == "true":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    # Optional: File handler for production
    if os.getenv("LOG_FILE"):
        file_handler = RotatingFileHandler(
            os.getenv("LOG_FILE"),
            maxBytes=10485760,  # 10MB
            backupCount=5,
        )
        file_handler.setLevel(getattr(logging, LOG_LEVEL))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter for logs."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)

        return json.dumps(log_entry)


def log_request_response(
    method: str,
    url: str,
    status_code: int,
    response_time: float,
    user_id: str = None,
    request_body: Dict[str, Any] = None,
    response_body: Dict[str, Any] = None
):
    """Log request/response information for monitoring.

    Args:
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        status_code: HTTP status code
        response_time: Time taken to process request in seconds
        user_id: User ID if authenticated
        request_body: Request body (optional)
        response_body: Response body (optional)
    """
    logger = setup_logging("monitoring.requests")

    extra_fields = {
        "method": method,
        "url": url,
        "status_code": status_code,
        "response_time_ms": round(response_time * 1000, 2),
        "user_id": user_id,
    }

    # Add request/response size info if available
    if request_body:
        extra_fields["request_size_bytes"] = len(json.dumps(request_body).encode('utf-8'))
    if response_body:
        extra_fields["response_size_bytes"] = len(json.dumps(response_body).encode('utf-8'))

    # Create a custom log record with extra fields
    record = logging.LogRecord(
        name=logger.name,
        level=logging.INFO,
        pathname='',
        lineno=0,
        msg=f"Request processed: {method} {url} -> {status_code} in {response_time:.3f}s",
        args=(),
        exc_info=None
    )
    record.extra_fields = extra_fields

    logger.handle(record)


def log_performance_metric(
    metric_name: str,
    value: float,
    unit: str = "ms",
    tags: Dict[str, str] = None
):
    """Log performance metrics for monitoring.

    Args:
        metric_name: Name of the metric
        value: Metric value
        unit: Unit of measurement (default: ms)
        tags: Additional tags for categorization
    """
    logger = setup_logging("monitoring.performance")

    extra_fields = {
        "metric_name": metric_name,
        "value": value,
        "unit": unit,
        "tags": tags or {}
    }

    record = logging.LogRecord(
        name=logger.name,
        level=logging.INFO,
        pathname='',
        lineno=0,
        msg=f"Performance metric: {metric_name} = {value}{unit}",
        args=(),
        exc_info=None
    )
    record.extra_fields = extra_fields

    logger.handle(record)


def log_database_operation(
    operation: str,
    table: str,
    duration: float,
    records_affected: int = None,
    query: str = None
):
    """Log database operations for performance monitoring.

    Args:
        operation: Operation type (SELECT, INSERT, UPDATE, DELETE)
        table: Table name
        duration: Query execution time in seconds
        records_affected: Number of records affected (for write operations)
        query: SQL query (optional, for debugging)
    """
    logger = setup_logging("monitoring.database")

    extra_fields = {
        "operation": operation.upper(),
        "table": table,
        "duration_ms": round(duration * 1000, 2),
        "records_affected": records_affected,
    }

    if query:
        extra_fields["query"] = query

    record = logging.LogRecord(
        name=logger.name,
        level=logging.INFO,
        pathname='',
        lineno=0,
        msg=f"DB operation: {operation} on {table} took {duration:.3f}s",
        args=(),
        exc_info=None
    )
    record.extra_fields = extra_fields

    logger.handle(record)


def log_ai_interaction(
    user_id: str,
    query: str,
    response: str,
    duration: float,
    model_used: str = None,
    tokens_used: int = None
):
    """Log AI interactions for monitoring and analytics.

    Args:
        user_id: User ID
        query: User's query to AI
        response: AI's response
        duration: Processing time in seconds
        model_used: AI model used (optional)
        tokens_used: Number of tokens used (optional)
    """
    logger = setup_logging("monitoring.ai")

    extra_fields = {
        "user_id": user_id,
        "query_length": len(query),
        "response_length": len(response),
        "duration_ms": round(duration * 1000, 2),
        "model": model_used,
        "tokens_used": tokens_used,
    }

    record = logging.LogRecord(
        name=logger.name,
        level=logging.INFO,
        pathname='',
        lineno=0,
        msg=f"AI interaction for user {user_id} took {duration:.3f}s",
        args=(),
        exc_info=None
    )
    record.extra_fields = extra_fields

    logger.handle(record)


# Global logger instance
logger = setup_logging("app")


# Alias for convenience
def get_logger(name: str = "app") -> logging.Logger:
    """Alias for setup_logging for convenience."""
    return setup_logging(name)
