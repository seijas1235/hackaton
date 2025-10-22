"""HTTP response helpers with CORS headers for API Gateway."""

from typing import Any, Dict, Optional
import json


def _cors_headers() -> Dict[str, str]:
    """Return standard CORS headers for API Gateway responses."""
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
    }


def ok(data: Any, status_code: int = 200) -> Dict[str, Any]:
    """Return a successful response with CORS headers.
    
    Args:
        data: Response payload (will be JSON-serialized)
        status_code: HTTP status code (default: 200)
        
    Returns:
        API Gateway proxy response dict
    """
    return {
        "statusCode": status_code,
        "headers": _cors_headers(),
        "body": json.dumps(data, default=str),
    }


def bad_request(message: str = "Bad Request", details: Optional[Any] = None) -> Dict[str, Any]:
    """Return a 400 Bad Request response with CORS headers.
    
    Args:
        message: Error message
        details: Optional additional error details
        
    Returns:
        API Gateway proxy response dict
    """
    body = {"error": message}
    if details is not None:
        body["details"] = details
    
    return {
        "statusCode": 400,
        "headers": _cors_headers(),
        "body": json.dumps(body, default=str),
    }


def unauthorized(message: str = "Unauthorized") -> Dict[str, Any]:
    """Return a 401 Unauthorized response with CORS headers.
    
    Args:
        message: Error message
        
    Returns:
        API Gateway proxy response dict
    """
    return {
        "statusCode": 401,
        "headers": _cors_headers(),
        "body": json.dumps({"error": message}),
    }


def server_error(message: str = "Internal Server Error", details: Optional[Any] = None) -> Dict[str, Any]:
    """Return a 500 Internal Server Error response with CORS headers.
    
    Args:
        message: Error message
        details: Optional additional error details (should not expose internals in production)
        
    Returns:
        API Gateway proxy response dict
    """
    body = {"error": message}
    if details is not None:
        body["details"] = details
    
    return {
        "statusCode": 500,
        "headers": _cors_headers(),
        "body": json.dumps(body, default=str),
    }
